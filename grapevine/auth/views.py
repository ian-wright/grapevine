from flask import Blueprint, render_template
from flask_security import Security, UserMixin, RoleMixin, login_required
from grapevine.auth.models import User
from grapevine.dynamo.models import Users


# instantiate table models
# TODO is this ok to float here?
users = Users()

user_manager = Blueprint('user_manager', __name__)

@user_manager.route('/')
def new_user():
    return 'this is home'


@user_manager.route('/create')
def create_user():
    # get a sample record and return it
    new_user = User(name='ian', email='ian@bloop.com')
    print('new user_id:', new_user.user_id)
    users.add(new_user)
    return 'saved a new user'


@user_manager.route('/get/<user_id>')
def get_user(user_id):
    try:
        retrieved_user = users.get(int(user_id))
        return str(retrieved_user)
    except ValueError:
        return 'no such user: %s' % user_id