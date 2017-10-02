from grapevine.security.models import User, Role
from grapevine.main.friends import Friendship
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime
import dateutil.parser


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
        # DynamoConn attributes are the correct access point for all dynamo tables
        self.user_table = UserTable(db.tables['USERS'])
        self.role_table = RoleTable(db.tables['ROLES'])
        self.friend_table = FriendTable(db.tables['FRIENDS'])

    def put_model(self, obj):
        """
        :param obj: an instance of any class with an existing associated dynamo table
        :return: the saved object, if successful

        NOTE: operation will completely replace an existing item with duplicate primary key
        """

        if isinstance(obj, User):
            if self.user_table.add(obj):
                return obj
        elif isinstance(obj, Role):
            if self.role_table.add(obj):
                return obj
        elif isinstance(obj, Friendship):
            if self.friend_table.add(obj):
                return obj
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
            return self.friend_table.delete(obj.email_1)
        else:
            raise TypeError("Cant delete model. No underlying DynamoDB table registered for type: \
                        {}".format(type(obj)))


class BaseTable:
    """abstract representation of a table in dynamoDB"""
    def __init__(self, underlying_dynamo_table):
        self.table = underlying_dynamo_table

    @classmethod
    def convert_attr_to_dynamo(cls, attr):
        """Supported value types for dynamo tables are:
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
        """Takes an dynamo-formatted attribute value as input,
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

        :param obj: an instance of User, Role, ect...
        :return: True for success, False for failure
        """
        new_item = {}
        for k, v in obj.__dict__.items():
            new_item[k] = self.convert_attr_to_dynamo(v)

        try:
            self.table.put_item(Item=new_item)
            print("added obj:", new_item)
            return True
        # TODO: what kind of errors thrown here?
        except:
            raise IOError("Couldn't write {} to DynamoDB".format(new_item))

        # self.table.put_item(Item=new_item)
        # print("added obj:", new_item)
        # return True

    def scan(self, **kwargs):
        """
        Performs an attribute scan over underlying table using specified params.

        :param kwargs: kwargs in form:
                attr_name1=attr_value1,
                attr_name2=attr_value2,
                ...
        :return: dictionary of instance attributes for single returned item, or None if no match
        """

        filter_list = [Attr(k).eq(self.convert_attr_to_dynamo(v)) for k, v in kwargs.items()]
        filter_expression = filter_list.pop()
        for cond in filter_list:
            # TODO: does this work?
            filter_expression &= cond
        try:
            response = self.table.scan(
                FilterExpression=filter_expression
            )
            if 'Items' in response:
                # assumes that the query is looking for a specific user (only one)
                return {k: self.convert_attr_from_dynamo(v) for k, v in response['Items'][0].items()}
        except:
            raise IOError("Couldn't scan {} on DynamoDB".format(filter_expression))

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
            # print('converted response dict:', converted_response)
            return class_type(**converted_response)

        # query() case
        if 'Items' in response:
            converted_response = {}
            for k, v in response['Items'][0].items():
                converted_response[k] = self.convert_attr_from_dynamo(v)
            # print('converted response dict:', converted_response)
            return class_type(**converted_response)


class UserTable(BaseTable):

    def get(self, email=None):
        """
        Queries dynamo for a specific user.

        :param email: email string
        :return: a User instance, or None if no match
        """
        try:
            response = self.table.get_item(
                Key={
                    'email': email
                }
            )
            return self.response_to_object(response, User)
        # TODO: error handling too broad
        except:
            raise IOError("Couldn't get user: <{}> from DynamoDB".format(email))

    def delete(self, email=None):
        """
        Deletes a specific user from dynamo.

        :param email: email string
        :return: True for success, or False for failure
        """
        try:
            self.table.delete_item(
                Key={
                    'email': email
                }
            )
            return True
        except:
            raise IOError("Couldn't delete {} from DynamoDB".format(email))

    def update(self, email=None, attr_name=None, attr_val=None):
        """ Updates one attribute at a time (documentation unclear if there is a syntax for more).

        :param email: primary key email for dynamo item to update
        :param attr_name: name of attribute to update
        :param attr_val: new attribute value
        :return: True for success, or False for failure
        """
        try:
            self.table.update_item(
                Key={
                    'email': email
                },
                UpdateExpression='SET {} = :val1'.format(attr_name),
                ExpressionAttributeValues={
                    ':val1': self.convert_attr_to_dynamo(attr_val)
                }
            )
            return True
        except:
            raise IOError("Couldn't update {}:{} for {} to DynamoDB".format(attr_name, attr_val, email))


class RoleTable(BaseTable):

    def get(self, name=None):
        """
        Queries dynamo for a specific role, by name.

        :param name: role name string
        :return: a Role instance, or False for failure
        """
        try:
            response = self.table.get_item(
                Key={
                    'name': name
                }
            )
            return self.response_to_object(response, Role)
        # TODO: error handling too broad
        except:
            raise IOError("Couldn't get role: <{}> from DynamoDB".format(name))

    def delete(self, name=None):
        """
        Deletes a specific role definition from dynamo.

        :param name: role name string
        :return: True, if successful
        """
        try:
            self.table.delete_item(
                Key={
                    'name': name
                }
            )
            return True
        except:
            raise IOError("Couldn't delete {} from DynamoDB".format(name))


class FriendTable(BaseTable):

    @staticmethod
    def _normalize_email_fields(response_item):
        if 'sender_email' in response_item:
            return response_item['sender_email']
        if 'receiver_email' in response_item:
            return response_item['receiver_email']

    def get_friendship(self, email_1, email_2):
        """
        Given a pair of email ids, return a Friendship instance, if exists
        :param email_1: First email in pair
        :param email_2: Second email in pair
        :return: Friendship instance, if it exists
        """
        print("trying to get friendship for {} + {}".format(email_1, email_2))
        try:
            # try sender-receiver combo first (can use get_item on primary hash)
            response_1 = self.table.get_item(
                Key={
                    'sender_email': email_1,
                    'receiver_email': email_2
                }
            )
            if 'Item' in response_1:
                return self.response_to_object(response_1, Friendship)

            # if that doesn't return anything, try receiver-sender combo (must use query on GSI)
            response_2 = self.table.query(
                IndexName='receiver-email-index',
                ExpressionAttributeValues={':v1': email_1, ':v2': email_2},
                KeyConditionExpression='receiver_email = :v1 AND sender_email = :v2'
            )
            if 'Items' in response_2 and len(response_2['Items']) == 1:
                return self.response_to_object(response_2, Friendship)

        except Exception as e:
            print("Couldn't get friendship for {} and {}".format(email_1, email_2))
            raise e

    def delete(self, email_1, email_2):
        """
        Given an unsorted pair of email ids, remove the associated Friendship record from the table.
        :param email_1: First email in pair
        :param email_2: Second email in pair
        :return: dict of attributes for deleted Friendship, if successful
        """
        try:
            # try sender-receiver combo first
            deleted_friendship_1 = self.table.delete_item(
                Key={
                    'sender_email': email_1,
                    'receiver_email': email_2
                },
                ReturnValues='ALL_OLD'
            )
            if 'Attributes' in deleted_friendship_1:
                return deleted_friendship_1

            # if that doesn't return anything, try receiver-sender combo (on GSI)
            deleted_friendship_2 = self.table.delete_item(
                Key={
                    'sender_email': email_2,
                    'receiver_email': email_1
                },
                ReturnValues='ALL_OLD'
            )
            if 'Attributes' in deleted_friendship_2:
                return deleted_friendship_2

        except Exception as e:
            print("Couldn't delete {} + {} Friendship from DynamoDB".format(email_1, email_2))
            raise e

    def list_confirmed_friends(self, email):
        """
        Given an email id, get a list of confirmed friends' emails (agnostic to who was sender vs receiver)
        :param email: Any email id
        :return: List of email ids for friends, or an empty list if no friends
        """
        try:
            # query against primary hash, and GSI hash, build and return list of friends
            sender_response = self.table.query(
                ExpressionAttributeValues={':v1': email},
                KeyConditionExpression='sender_email = :v1',
                ProjectionExpression='receiver_email, confirmed_at'
            )
            receiver_response = self.table.query(
                IndexName='receiver-email-index',
                ExpressionAttributeValues={':v1': email},
                KeyConditionExpression='receiver_email = :v1',
                ProjectionExpression='sender_email, confirmed_at'
            )
            response = sender_response.get('Items', []) + receiver_response.get('Items', [])
            confirmed_response = filter(lambda item: item['confirmed_at'] is not None, response)
            return [self._normalize_email_fields(item) for item in confirmed_response]
        except Exception as e:
            print("Couldn't list confirmed friends for {}".format(email))
            raise e

    def list_pending_received_requests(self, receiver_email):
        """
        Given an email id for a receiving user, get a list of all pending friend requests (sender emails)
        :param receiver_email: email for request-receiving user
        :return: list of email ids for senders of pending requests
        """
        try:
            receiver_response = self.table.query(
                IndexName='receiver-email-index',
                ExpressionAttributeValues={':v1': receiver_email},
                KeyConditionExpression='receiver_email = :v1',
                ProjectionExpression='sender_email, confirmed_at'
            )
            response = receiver_response.get('Items', [])
            confirmed_response = filter(lambda item: 'confirmed_at' not in item, response)
            return [self._normalize_email_fields(item) for item in confirmed_response]
        except Exception as e:
            print("Couldn't list pending requests sent to {}".format(receiver_email))
            raise e

    def list_pending_sent_requests(self, sender_email):
        """
        Given an email id for a sending user, get a list of all pending friend requests (receiver emails)
        :param sender_email: email for request-sending user
        :return: list of email ids for receivers of pending requests
        """
        try:
            sender_response = self.table.query(
                ExpressionAttributeValues={':v1': sender_email},
                KeyConditionExpression='sender_email = :v1',
                ProjectionExpression='receiver_email, confirmed_at'
            )
            response = sender_response.get('Items', [])
            confirmed_response = filter(lambda item: item['confirmed_at'] is None, response)
            return [self._normalize_email_fields(item) for item in confirmed_response]
        except Exception as e:
            print("Couldn't list pending requests sent by {}".format(sender_email))
            raise e

