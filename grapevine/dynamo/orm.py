from datetime import datetime

import dateutil.parser
from boto3.dynamodb.conditions import Attr

from grapevine.friends.friends import Friendship
from grapevine.security.models import User, Role
from grapevine.shares.shares import Article, Share


class DynamoConn:
    """top-level model to encapsulate a 'connection' to DynamoDB,
     and provide all related models and transactional methods to interface with
     DynamoDB tables.

     This emulates an ORM, in that any object that fits into the existing schema
     can be created, deleted, updated, or retrieved.

     Use table attributes directly for add/get/delete/update with an object of known type.
     Use put_model and delete_model methods for arbitrary objects of unknown type (which map to correct tables).

     :param db: A flask-dynamo object, already initialized on the app.
     """

    def __init__(self, db):
        """
        :param db: a flask-security DynamoDatastore
        """
        # DynamoConn attributes are the correct access point for all dynamo tables
        self.role_table = RoleTable(db.tables['ROLES'])
        self.user_table = UserTable(db.tables['USERS'], self.role_table)
        self.friend_table = FriendTable(db.tables['FRIENDS'])
        self.article_table = ArticleTable(db.tables['ARTICLES'])
        self.share_table = ShareTable(db.tables['SHARES'])

    @staticmethod
    def _role_object_to_str(role):
        """
        convert a flask-security role object to its name string representation, if necessary
        :param role: role object OR role name string
        :return: role name string
        """
        if isinstance(role, Role):
            return role.name
        else:
            return role

    def put_model(self, obj):
        """
        :param obj: an instance of any class with an existing associated dynamo table
        :return: the saved object, if successful

        NOTE: operation will completely replace an existing item with duplicate primary key
        """
        if isinstance(obj, User):
            # convert list of role objects to role name strings
            # this is required for flask-security to manage roles properly
            obj.roles = list(map(self._role_object_to_str, obj.roles))
            if self.user_table.add(obj):
                # now flip them back to objects for a return value on put_item success!
                return self.user_table.objectify_role_strings(obj)
        elif isinstance(obj, Role):
            return self.role_table.add(obj)
        elif isinstance(obj, Friendship):
            return self.friend_table.add(obj)
        elif isinstance(obj, Article):
            return self.article_table.add(obj)
        elif isinstance(obj, Share):
            return self.share_table.add(obj)
        else:
            raise TypeError("Cant add model. No underlying DynamoDB table registered for type: \
            {}".format(type(obj)))

    def delete_model(self, obj):
        """
        :param obj: an instance of any class with an existing associated dynamo table
        :return: True for success, False for failure
        """
        if isinstance(obj, User):
            return self.user_table.delete(obj.email)
        elif isinstance(obj, Role):
            return self.role_table.delete(obj.name)
        elif isinstance(obj, Friendship):
            return self.friend_table.delete(obj.sender_email, obj.receiver_email)
        elif isinstance(obj, Article):
            return self.article_table.delete_article(obj.url)
        elif isinstance(obj, Share):
            return self.share_table.delete_share(obj.sender_email, obj.receiver_email, obj.url)
        else:
            raise TypeError("Cant delete model. No underlying DynamoDB table registered for type: \
                        {}".format(type(obj)))


class BaseTable(object):
    # abstract representation of a table in dynamoDB
    def __init__(self, underlying_dynamo_table):
        self.table = underlying_dynamo_table

    @classmethod
    def convert_attr_to_dynamo(cls, attr):
        """
        Supported value types for dynamo tables are:
        STRING = 'S'
        NUMBER = 'N'
        BINARY = 'B'
        STRING_SET = 'SS'
        NUMBER_SET = 'NS'
        BINARY_SET = 'BS'
        NULL = 'NULL'
        BOOLEAN = 'BOOL'
        MAP = 'M'
        LIST = 'L'

        This utility method takes any attribute value as input, and converts it to a
        dynamo-usable value.

        :param attr: raw attribute value
        :return: converted/cleaned attribute value
        """
        # timestamp case
        if isinstance(attr, datetime):
            return attr.isoformat()
        # all other cases
        else:
            return attr

    @classmethod
    def convert_attr_from_dynamo(cls, attr):
        """
        Takes an dynamo-formatted attribute value as input,
        and converts it to it's useful pythonic format.

        :param attr: dynamo attribute value
        :return: pythonic attribute value
        """
        try:
            datetime_obj = dateutil.parser.parse(attr)
            return datetime_obj
        # TODO - this is probably bad practice to catch errors as flow control
        except (ValueError, TypeError):
            return attr

    def add(self, obj):
        """
        Call put_item() on any compatible object to its corresponding DynamoDB table.

        :param obj: an instance of User, Role, ect...
        :return: the added object, if successful
        """
        # create a dict with instance variables only
        new_item = {}
        for k, v in obj.__dict__.items():
            new_item[k] = self.convert_attr_to_dynamo(v)

        if self.table.put_item(Item=new_item):
            print("added obj:", obj, vars(obj))
            return True

    def scan(self, **kwargs):
        """
        Performs an attribute scan (outside of primary key and GSI) over underlying table using specified params.

        :param kwargs: kwargs in form:
                attr_name1=attr_value1,
                attr_name2=attr_value2,
                ...
        :return: dictionary of instance attributes for single returned item, or None if no match
        """
        # TODO: tests this method! for user objects, must convert role list from strings to role objects
        filter_list = [Attr(k).eq(self.convert_attr_to_dynamo(v)) for k, v in kwargs.items()]
        filter_expression = filter_list.pop()
        for cond in filter_list:
            filter_expression &= cond

        response = self.table.scan(FilterExpression=filter_expression)
        if 'Items' in response:
            # assumes that the query is looking for a specific user (only one)
            return {k: self.convert_attr_from_dynamo(v) for k, v in response['Items'][0].items()}

    def response_to_object(self, response, class_type):
        """
        Builds an instance of given class from the dictionary returned by DynamoDB's get_item, if exists.
        :param response: Dynamo response dict
        :param class_type: Class type of output object (Role, User, ect)
        :return: Instance of class type, if it exists
        """

        # get_item() case
        if 'Item' in response:
            converted_response = {}
            for k, v in response['Item'].items():
                converted_response[k] = self.convert_attr_from_dynamo(v)
            return class_type(**converted_response)

        # delete_item() case
        if 'Attributes' in response:
            converted_response = {}
            for k, v in response['Attributes'].items():
                converted_response[k] = self.convert_attr_from_dynamo(v)
            return class_type(**converted_response)

        # query() case
        if 'Items' in response:
            converted_response = {}
            for k, v in response['Items'][0].items():
                converted_response[k] = self.convert_attr_from_dynamo(v)
            return class_type(**converted_response)


class UserTable(BaseTable):

    def __init__(self, underlying_dynamo_table, role_table_model):
        super().__init__(underlying_dynamo_table)
        self.role_table_model = role_table_model

    def _role_str_to_obj(self, role):
        if isinstance(role, Role):
            return role
        else:
            return self.role_table_model.get(role)

    def objectify_role_strings(self, user):
        # convert the user's list of assigned roles from role name strings to real user objects

        if len(user.roles) > 0:
            user.roles = list(map(self._role_str_to_obj, user.roles))
            return user
        return user

    # TODO - rename to get_user
    def get(self, email):
        """
        Queries dynamo for a specific user.

        :param email: email string
        :return: a User instance, or None if no match
        """
        response = self.table.get_item(Key={'email': email})
        user = self.response_to_object(response, User)
        if user:
            return self.objectify_role_strings(user)

    # TODO - rename to delete_user
    def delete(self, email):
        """
        Deletes a specific user from dynamo.

        :param email: email string
        :return: True for success, or False for failure
        """
        deleted_user = self.table.delete_item(
            Key={'email': email},
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in deleted_user:
            return self.response_to_object(deleted_user, User)

    # TODO - rename to update_user
    def update(self, email=None, attr_name=None, attr_val=None):
        """ Updates one attribute at a time (documentation unclear if there is a syntax for more).

        :param email: primary key email for dynamo item to update
        :param attr_name: name of attribute to update
        :param attr_val: new attribute value
        :return: True for success, or False for failure
        """
        # TODO: tests this method! be aware of role string-object conversion; maybe just kill this method
        updated_user = self.table.update_item(
            Key={'email': email},
            UpdateExpression='SET {} = :val1'.format(attr_name),
            ExpressionAttributeValues={':val1': self.convert_attr_to_dynamo(attr_val)},
            ReturnValues='ALL_NEW'
        )
        if 'Attributes' in updated_user:
            return self.response_to_object(updated_user, User)


class RoleTable(BaseTable):

    # TODO - rename to get_role
    def get(self, name=None):
        """
        Queries dynamo for a specific role, by name.

        :param name: role name string
        :return: a Role instance, or False for failure
        """
        response = self.table.get_item(Key={'name': name})
        role = self.response_to_object(response, Role)
        if role:
            return role

    # TODO - rename to delete_role
    def delete(self, name=None):
        """
        Deletes a specific role definition from dynamo.

        :param name: role name string
        :return: True, if successful
        """
        deleted_role = self.table.delete_item(
            Key={'name': name},
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in deleted_role:
            return self.response_to_object(deleted_role, Role)


class FriendTable(BaseTable):

    @staticmethod
    def _extract_normalized_email(response_item):
        """

        :param response_item:
        :return:
        """
        if 'sender_email' in response_item:
            return response_item['sender_email']
        if 'receiver_email' in response_item:
            return response_item['receiver_email']

    def get_friendship(self, email_1, email_2):
        """
        Given a pair of email ids, return a Friendship instance, if exists (agnostic to sender vs. receiver)
        :param email_1: First email in pair
        :param email_2: Second email in pair
        :return: Friendship instance, if it exists
        """
        print("trying to get friendship for {} + {}".format(email_1, email_2))

        # try sender-receiver combo first (can use get_item on primary hash)
        response_1 = self.table.get_item(Key={
            'sender_email': email_1,
            'receiver_email': email_2
        })
        if 'Item' in response_1:
            return self.response_to_object(response_1, Friendship)

        # if that doesn't return anything, try receiver-sender combo (have to use 'query' on GSI)
        response_2 = self.table.query(
            IndexName='receiver_email_index',
            ExpressionAttributeValues={':re': email_1, ':se': email_2},
            KeyConditionExpression='receiver_email = :re AND sender_email = :se'
        )
        if 'Items' in response_2 and len(response_2['Items']) == 1:
            return self.response_to_object(response_2, Friendship)

    # TODO - rename to delete_friendship
    def delete(self, email_1, email_2):
        """
        Given an unsorted pair of email ids, remove the associated Friendship record from the table.
        :param email_1: First email in pair
        :param email_2: Second email in pair
        :return: dict of attributes for deleted Friendship, if successful
        """
        # try sender-receiver combo first
        deleted_friendship_1 = self.table.delete_item(
            Key={
                'sender_email': email_1,
                'receiver_email': email_2
            },
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in deleted_friendship_1:
            return self.response_to_object(deleted_friendship_1, Friendship)

        # if that doesn't return anything, try receiver-sender combo (on GSI)
        deleted_friendship_2 = self.table.delete_item(
            Key={
                'sender_email': email_2,
                'receiver_email': email_1
            },
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in deleted_friendship_2:
            return self.response_to_object(deleted_friendship_2, Friendship)

    def list_confirmed_friends(self, email):
        """
        Given an email id, get a list of confirmed friends' emails (agnostic to who was sender vs receiver)

        :param email: Any email id
        :return: List of email ids for friends, or an empty list if no friends
        """
        # query against primary hash, and GSI hash, build and return list of friends
        sender_response = self.table.query(
            ExpressionAttributeValues={':se': email},
            KeyConditionExpression='sender_email = :se',
            ProjectionExpression='receiver_email, confirmed_at'
        )
        receiver_response = self.table.query(
            IndexName='receiver_email_index',
            ExpressionAttributeValues={':re': email},
            KeyConditionExpression='receiver_email = :re',
            ProjectionExpression='sender_email, confirmed_at'
        )
        response = sender_response.get('Items', []) + receiver_response.get('Items', [])
        confirmed_response = [item for item in response if item['confirmed_at'] is not None]

        return [self._extract_normalized_email(item) for item in confirmed_response]

    def list_pending_received_requests(self, receiver_email):
        """
        Given an email id for a receiving user, get a list of all pending friend requests (sender emails)

        :param receiver_email: email for request-receiving user
        :return: list of email ids for senders of pending requests
        """
        receiver_response = self.table.query(
            IndexName='receiver_email_index',
            ExpressionAttributeValues={':re': receiver_email},
            KeyConditionExpression='receiver_email = :re',
            ProjectionExpression='sender_email, confirmed_at'
        )
        response = receiver_response.get('Items', [])
        pending_response = [item for item in response if item['confirmed_at'] is None]

        return [self._extract_normalized_email(item) for item in pending_response]

    def list_pending_sent_requests(self, sender_email):
        """
        Given an email id for a sending user, get a list of all pending friend requests (receiver emails)

        :param sender_email: email for request-sending user
        :return: list of email ids for receivers of pending requests
        """
        sender_response = self.table.query(
            ExpressionAttributeValues={':se': sender_email},
            KeyConditionExpression='sender_email = :se',
            ProjectionExpression='receiver_email, confirmed_at'
        )
        response = sender_response.get('Items', [])
        pending_response = [item for item in response if item['confirmed_at'] is None]

        return [self._extract_normalized_email(item) for item in pending_response]


class ArticleTable(BaseTable):

    def get_article(self, url):
        response = self.table.get_item(Key={'url': url})
        if 'Item' in response:
            return self.response_to_object(response, Article)

    def delete_article(self, url):
        deleted_article = self.table.delete_item(
            Key={'url': url},
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in deleted_article:
            return self.response_to_object(deleted_article, Article)


class ShareTable(BaseTable):

    def get_share(self, sender_email, receiver_email, url):
        response = self.table.get_item(Key={
            'email_key': sender_email + ',' + receiver_email,
            'url': url
        })
        if 'Item' in response:
            return self.response_to_object(response, Article)

    def delete_share(self, sender_email, receiver_email, url):
            deleted_article = self.table.delete_item(
                Key={'url': url},
                ReturnValues='ALL_OLD'
            )
            if 'Attributes' in deleted_article:
                return self.response_to_object(deleted_article, Article)

    # def list_re