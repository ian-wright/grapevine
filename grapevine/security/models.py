from flask_security import UserMixin, RoleMixin
from flask_security.datastore import UserDatastore
from flask_security.utils import string_types


class User(UserMixin):

    def __init__(self, attr_dict=None, **kwargs):
        """
        :param kwargs: must include:
                    - email
                    - password
                    - first_name
                    - last_name
        """

        # self.active (bool) (injected by UserDatastore._prepare_create_user_args)

        # self.roles ([Role.name string]) (injected by UserDatastore._prepare_create_user_args)
        # flask-security role functionality
        # roles are stored in db by only their string names, but converted to role objects in app environment

        args = attr_dict or kwargs

        # registration form fields
        self.email = args.get('email')
        self.password = args.get('password')
        self.first_name = args.get('first_name')
        self.last_name = args.get('last_name')
        self.roles = args.get('roles', [])

        # flask-security needs a unique user ID, so email is used again
        self.id = args['email']

        # flask-security confirmable
        self.confirmed_at = args.get('confirmed_at', None)

        # flask-security trackable
        self.last_login_at = args.get('last_login_at', None)
        self.current_login_at = args.get('current_login_at', None)
        self.last_login_ip = args.get('last_login_ip', None)
        self.current_login_ip = args.get('current_login_ip', None)
        self.login_count = args.get('login_count', 0)

    # Custom User Payload
    def get_security_payload(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }


class Role(RoleMixin):
    """Just two possible roles:
    {'name: 'pleb', 'description': 'regular user'}
    {'name: 'royal', 'description': 'administrator'}
    """
    def __init__(self, attr_dict=None, **kwargs):
        args = attr_dict or kwargs
        self.name = args.get('name')
        self.description = args.get('description')


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
    def put(self, model):
        """ write an object to dynamoDB;
        must be agnostic to which model type is being added
        (simulate behaviour of an ORM, where each model type
        is already registered with the db connection object)
        """
        # TODO: is this true-false return paradigm for all the IO methods in dynamo and security models useful?
        if self.dynamo_conn.put_model(model):
            return model
        else:
            return False

    def delete(self, model):
        """ delete an object from dynamoDB;
        must be agnostic to which model type is being added
        (simulate behaviour of an ORM, where each model type
        is already registered with the db connection object)
        """
        if self.dynamo_conn.delete_model(model):
            return True
        else:
            return False


class DynamoUserDatastore(DynamoDatastore, UserDatastore):
    """A DynamoDB user datastore implementation for Flask-Security """

    def __init__(self, dynamo_conn, user_model, role_model):
        # dynamo_conn: an instance of DynamoConn class
        DynamoDatastore.__init__(self, dynamo_conn)
        # user/role_model: class definitions for User and Role
        UserDatastore.__init__(self, user_model, role_model)

    # overridden to replace find_user with get_user (dynamo scan operations are very expensive)
    def _prepare_role_modify_args(self, user, role):
        if isinstance(user, string_types):
            user = self.get_user(email=user)
        if isinstance(role, string_types):
            role = self.find_role(name=role)
        return user, role

    def get_user(self, email):
        """
        Fetches a user matching the specified email address, if exists.

        :param email: email string to search for
        :return: instance of User class, or None if no match
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
        :return: instance of User class, or False if no match
        """

        # if kwargs only contains the primary ID (email), revert to more efficient get_user method
        if len(kwargs) == 1 and 'email' in kwargs:
            return self.get_user(kwargs['email'])
        elif len(kwargs) == 1 and 'id' in kwargs:
            return self.get_user(kwargs['id'])
        # otherwise, scan the table for attribute value matches
        else:
            print("FINDING with scan")
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

    # overridden to ensure that only role names are listed on user.roles
    # default implementation writes entire role object
    def add_role_to_user(self, user, role):
        """Adds a role to a user.

        :param user: The user to manipulate
        :param role: The role to add to the user
        """
        user, role = self._prepare_role_modify_args(user, role)

        # if role.name not in [role.name for role in user.roles]:
        if role not in user.roles:
            user.roles.append(role)
            return self.put(user)

    def remove_role_from_user(self, user, role):
        """Removes a role from a user.

        :param user: The user to manipulate
        :param role: The role to remove from the user
        """
        rv = False
        user, role = self._prepare_role_modify_args(user, role)
        if role.name in [role.name for role in user.roles]:
            user.roles.remove(role)
            self.put(user)
        return rv
