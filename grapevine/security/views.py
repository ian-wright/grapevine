from flask import Blueprint, render_template
from grapevine.security.models import User


user_manager = Blueprint('user_manager', __name__)


# helper function that builds a dynamo connector based on app configuration
# accessible from within blueprint views
##  def get_db():
#     if current_app.config['LOCAL_DYNAMO']:
#         return DynamoConn(local=True)
#     else:
#         return DynamoConn()




    # add more table models here


@user_manager.route('/')
def new_user():
    return 'this is home'


@user_manager.route('/create')
def create_user():
    # get a sample record and return it
    user_table = get_table('USERS')
    new_user = User(email='ian@bloop.com', first_name='Ian', last_name='Wright')
    print('new user email:', new_user.email)
    user_table.add(new_user)
    return 'saved a new user'


@user_manager.route('/get/<user_id>')
def get_user(user_id):
    user_table = get_table('USERS')
    try:
        retrieved_user = user_table.get(int(user_id))
        return str(retrieved_user)
    except ValueError:
        return 'no such user: %s' % user_id
