from grapevine.security.models import User, Role
from boto3.dynamodb.conditions import Attr
from datetime import datetime
import dateutil.parser


class DynamoConn:
    """top-level model to encapsulate a 'connection' to DynamoDB,
     and provide all related models and transactional methods to interface with
     DynamoDB tables.

     This simulates an ORM, in that any object that fits into the existing schema
     can be created, deleted, updated, or retrieved.

     Use table attributes directly for add/get/delete/update with an object of known type.
     Use put_model and delete_model methods for arbitrary objects of unknown type (which map to correct tables).

     :param db: A flask-dynamo object, already initialized on the app.
     """

    def __init__(self, db):
        self.user_table = UserTable(db.tables['USERS'])
        self.role_table = RoleTable(db.tables['ROLES'])

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

        # try:
        #     self.table.put_item(Item=new_item)
        #     print("added obj:", new_item)
        #     return True
        # # TODO: what kind of errors thrown here?
        # except:
        #     raise IOError("Couldn't write {} to DynamoDB".format(new_item))

        self.table.put_item(Item=new_item)
        print("added obj:", new_item)
        return True

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
            filter_expression &= cond
        # try:
        #     response = self.table.scan(
        #         # TODO: does this work?
        #         FilterExpression=filter_expression
        #     )
        #     if 'Items' in response:
        #         # assumes that the query is looking for a specific user (only one)
        #         return {k: self.convert_attr_from_dynamo(v) for k, v in response['Items'][0].items()}
        # except:
        #     raise IOError("Couldn't scan {} on DynamoDB".format(filter_expression))

        response = self.table.scan(
            # TODO: does this work?
            FilterExpression=filter_expression
        )
        if 'Items' in response:
            # assumes that the query is looking for a specific user (only one)
            return {k: self.convert_attr_from_dynamo(v) for k, v in response['Items'][0].items()}


class UserTable(BaseTable):

    def get(self, email=None):
        """
        Queries dynamo for a specific user.

        :param email: email string
        :return: a User instance, or None if no match
        """
        # try:
        #     response = self.table.get_item(
        #         Key={
        #             'email': email
        #         }
        #     )
        #     if response['Item']:
        #         converted_response = {}
        #         for k, v in response['Item'].items():
        #             converted_response[k] = self.convert_attr_from_dynamo(v)
        #
        #         return User(attr_dict=converted_response)
        # # TODO: error handling too broad
        # except:
        #     raise IOError("Couldn't get user: <{}> from DynamoDB".format(email))

        response = self.table.get_item(
            Key={
                'email': email
            }
        )
        if 'Item' in response:
            converted_response = {}
            for k, v in response['Item'].items():
                converted_response[k] = self.convert_attr_from_dynamo(v)

            return User(attr_dict=converted_response)

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
            return Role(attr_dict=response['Item'])
        # TODO: error handling too broad
        except:
            raise IOError("Couldn't get role: <{}> from DynamoDB".format(name))

    def delete(self, name=None):
        """
        Deletes a specific role definition from dynamo.

        :param name: role name string
        :return: True for success, or False for failure
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

