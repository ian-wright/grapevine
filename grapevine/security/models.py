from flask_security import UserMixin, RoleMixin
from flask_security.datastore import UserDatastore
from flask_security.utils import string_types


class User(UserMixin):
    # registration form fields
    email = None
    password = None
    first_name = None
    last_name = None

    # flask-security confirmable
    confirmed_at = None

    # flask-security trackable
    last_login_at = None
    current_login_at = None
    last_login_ip = None
    current_login_ip = None
    login_count = None

    def __init__(self, attr_dict=None, **kwargs):
        """
        :param kwargs: must include:
                    - email
                    - password
                    - first_name
                    - last_name
                    - active (bool) (injected by UserDatastore._prepare_create_user_args)
                    - roles ([Role objects]) (injected by UserDatastore._prepare_create_user_args)
        """
        args = attr_dict or kwargs
        for k, v in args.items():
            setattr(self, k, v)
        # flask-security needs a unique id, so email is used again
        self.id = args['email']

    # Custom User Payload
    def get_security_payload(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }


class Role(RoleMixin):
    """Just two possible roles:
    {'id': 0, 'name: 'pleb', 'description': 'regular user'}
    {'id': 1, 'name: 'royal', 'description': 'administrator'}
    """
    def __init__(self, attr_dict=None, **kwargs):
        """
        :param kwargs: must include:
                    - id
                    - name
                    - description
        """
        args = attr_dict or kwargs
        for k, v in args.items():
            setattr(self, k, v)


class Datastore(object):
    """Abstract base level datastore object.
    :param dynamo_conn: An instance of the DynamoConn ORM emulator
    """
    def __init__(self, dynamo_conn):
        self.dynamo_conn = dynamo_conn

    def commit(self):
        # 'commit' method doesn't need to be implemented
        # (flask-dynamo doesn't use sessions or commits)
        pass

    def put(self, model):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError


class DynamoDatastore(Datastore):
    """
    :param dynamo_conn: An instance of the DynamoConn ORM emulator
    """
    def put(self, model):
        """ write an object to dynamoDB;
        must be agnostic to which model type is being added
        (simulate behaviour of an ORM, where each model type
        is already registered with the db connection object)
        """
        # TODO: is this true-false return paradigm for all the IO methods in dynamo and security models useful?
        if self.dynamo_conn.put_model(model):
            return model
        # else:
        #     return False

    def delete(self, model):
        """ delete an object from dynamoDB;
        must be agnostic to which model type is being added
        (simulate behaviour of an ORM, where each model type
        is already registered with the db connection object)
        """
        if self.dynamo_conn.delete_model(model):
            return True
        # else:
        #     return False


class DynamoUserDatastore(DynamoDatastore, UserDatastore):
    """A DynamoDB user datastore implementation for Flask-Security """

    def __init__(self, dynamo_conn, user_model, role_model):
        # dynamo_conn: an instance of DynamoConn class
        DynamoDatastore.__init__(self, dynamo_conn)
        # user/role_model: class definitions for User and Role
        UserDatastore.__init__(self, user_model, role_model)

    def _prepare_role_modify_args(self, user, role):
        if isinstance(user, string_types):
            # overridden to replace find_user with get_user (scan operations too expensive)
            user = self.get_user(email=user)
        if isinstance(role, string_types):
            role = self.find_role(name=role)
        return user, role

    def get_user(self, email):
        """
        Fetches a user matching the specified email address, if exists.

        :param email: email string to search for
        :return: instance of User class, if exists
        """
        user = self.dynamo_conn.user_table.get(email=email)
        if user:
            return user

    def find_user(self, **kwargs):
        """
        Fetches a user matching the provided params, if exists.

        :param kwargs: kwargs in form:
                attr_name1=attr_value1,
                attr_name2=attr_value2,
                ...
        :return: instance of User class, if exists
        """
        user_attr_dict = self.dynamo_conn.user_table.scan(**kwargs)
        if user_attr_dict:
            return User(attr_dict=user_attr_dict)

    def find_role(self, name):
        """
        Fetches a role definition matching the specified role name, if exists.

        :param name: role name string to search for
        :return: instance of Role class, if exists
        """
        role = self.dynamo_conn.role_table.get(name=name)
        if role:
            return role
