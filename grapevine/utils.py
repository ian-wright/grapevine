from werkzeug.local import LocalProxy
from grapevine.dynamo.orm import DynamoConn
from grapevine.friends.friends import FriendManager


def get_connection(app):
    # with an application context present, get a connection to our db
    _dyn = LocalProxy(lambda: app.extensions['dynamo'])
    # ORM object
    _db = DynamoConn(_dyn)
    # Friend Manager object
    _friends = FriendManager(_db)
    # flask-security extension
    _security = LocalProxy(lambda: app.extensions['security'])
    # user datastore required for flask-security
    _userdata = LocalProxy(lambda: _security.datastore)
    return _dyn, _db, _friends, _userdata