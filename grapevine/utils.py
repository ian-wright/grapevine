from werkzeug.local import LocalProxy
from grapevine.dynamo.orm import DynamoConn
from grapevine.friends.friends import FriendManager
from grapevine.shares.shares import ShareManager


def get_connection(app):
    # with an application context present, get a connection to our db
    _dyn = LocalProxy(lambda: app.extensions['dynamo'])
    # ORM object
    _db = DynamoConn(_dyn)
    # FriendManager instance
    _friends = FriendManager(_db)
    # ShareManager instance
    _shares = ShareManager(_db)
    # flask-security extension
    _security = LocalProxy(lambda: app.extensions['security'])
    # user datastore required for flask-security
    _users = LocalProxy(lambda: _security.datastore)
    return {
        '_dyn': _dyn,
        '_db': _db,
        '_users': _users,
        '_friends': _friends,
        '_shares': _shares
    }