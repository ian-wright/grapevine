from flask import Blueprint, render_template
from flask import current_app
from flask_security import Security, UserMixin, RoleMixin, login_required
from grapevine.auth.models import User
from grapevine.dynamo.connection import DynamoConn


user_manager = Blueprint('user_manager', __name__)


def get_db():
    if current_app.config['LOCAL_DYNAMO']:
        return DynamoConn(local=True)
    else:
        return DynamoConn()


@user_manager.route('/')
def new_user():
    return 'this is home'


@user_manager.route('/create')
def create_user():
    # get a sample record and return it
    db = get_db()
    new_user = User(name='ian', email='ian@bloop.com')
    print('new user_id:', new_user.user_id)
    db.user_table.add(new_user)
    return 'saved a new user'


@user_manager.route('/get/<user_id>')
def get_user(user_id):
    db = get_db()
    try:
        retrieved_user = db.user_table.get(int(user_id))
        return str(retrieved_user)
    except ValueError:
        return 'no such user: %s' % user_id
