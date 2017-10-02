from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from flask_security.decorators import login_required
from flask_security.utils import logout_user, hash_password
from flask_security.core import current_user
from werkzeug.local import LocalProxy
from grapevine.dynamo.models import DynamoConn
from grapevine.main.friends import FriendManager
from validate_email import validate_email


# useful instance variables
# flask-dynamo extension
#with current_app.app_context():
# _dynamo = LocalProxy(lambda: current_app.extensions['dynamodb'])
# # ORM object
# _db = DynamoConn(_dynamo)
# _fm = FriendManager(_db)

# # flask-security extension
# _security = LocalProxy(lambda: current_app.extensions['security'])
# # user_datastore required for flask-security
# _user_datastore = LocalProxy(lambda: _security.datastore)

main_bp = Blueprint('main_bp', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')


def get_connection(ctx):

    # with an application context present, get a connection to our db
    _dyn = LocalProxy(lambda: ctx.extensions['dynamo'])
    # ORM object
    _db = DynamoConn(_dyn)
    # Friend Manager object
    _friends = FriendManager(_db)
    # flask-security extension
    _security = LocalProxy(lambda: ctx.extensions['security'])
    # user datastore required for flask-security
    _userdata = LocalProxy(lambda: _security.datastore)
    return _dyn, _db, _friends, _userdata


# @main_bp.before_app_first_request
def before_first_request():

    with current_app.app_context():
        print('current app:', current_app)
        _dyn, _db, _friends, _userdata = get_connection(current_app)

        # Create any database tables that don't exist yet.
        # with current_app.app_context():
        #     _dynamo = LocalProxy(lambda: current_app.extensions['dynamodb'])
        #     _dynamo.create_all()
        _dyn.create_all()

        # Create the admin role (royal) and end-user role (pleb), unless they already exist
        _userdata.find_or_create_role(id=0, name='royal', description='administrator')
        _userdata.find_or_create_role(id=1, name='pleb', description='end user')

        # Create two Users for testing purposes, unless they already exist.
        encrypted_password = hash_password('password')
        if not _userdata.get_user('ian.f.t.wright@gmail.com'):
            _userdata.create_user(
                email='ian.f.t.wright@gmail.com',
                password=encrypted_password,
                first_name='Ian-Admin',
                last_name='Wright'
            )
        if not _userdata.get_user('iw453@nyu.edu'):
            _userdata.create_user(
                email='iw453@nyu.edu',
                password=encrypted_password,
                first_name='Ian-User',
                last_name='Wright'
            )

        # assign roles to users, if they're not already assigned
        _userdata.add_role_to_user('iw453@nyu.edu', 'pleb')
        _userdata.add_role_to_user('ian.f.t.wright@gmail.com', 'royal')


# TODO - look into enabling token-based authentication with flask-security
@main_bp.route('/', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST' and 'logout' in request.form:
        print('logging user out...')
        logout_user()
        return redirect(url_for('security.login'))

    _dyn, _db, _friends, _userdata = get_connection(current_app)

    pending_friends = _friends.list_pending_requests_users(current_user.email)
    return render_template(
        'main/home.html',
        pending_friends=pending_friends,
        current_user_dict=current_user.get_security_payload()

    )


# TODO - consider breaking friend-stuff out into its own blueprint
@main_bp.route('/add-friend', methods=['POST'])
@login_required
def add_friend():
    """
    Takes an email address as JSON from a client-side ajax post request, validates the email,
    and either:
        - asks for a valid email (if necessary)
        - sees that the requested user is already a friend of the current user
        - sees an existing GV user with the requested email and sends a friend request email
        - determines that the requested email isn't yet in the db, and sends an app invite email to the new user.
    :return: feedback message to client for immediate display beside form
    """
    _dyn, _db, _friends, _userdata = get_connection(current_app)

    target_email = request.json['target_email']
    target_user = _userdata.get_user(target_email)

    if target_user and _db.friend_table.get_friendship(current_user.email, target_email):
        # case: Requested user is already one of the current user's friends.
        user_message = "{} is already in your friend list.".format(target_user.first_name)

    elif target_user and not _db.friend_table.get_friendship(current_user.email, target_email):
        # case: Valid email, GV account exists; send a friend request.
        _friends.send_friend_request_existing(sender_user=current_user, receiver_email=target_email)
        user_message = "We sent {} your connection request.".format(target_user.first_name)

    elif not target_user and validate_email(target_email):
        # case: Valid email, but no account on GV yet; send an app invite w/ special friend request copy.
        #       Upon account confirmation, redirect to the friend accept view.
        _friends.send_app_friend_request(sender_user=current_user, receiver_email=target_email)
        user_message = "There's no Grapevine account for {} yet. \
            We sent an app invite with your connection request.".format(target_email)

    else:
        # case: invalid email address
        user_message = "Please provide a valid email address."

    return user_message


@main_bp.route('/confirm-friend-request', methods=['POST'])
@login_required
def confirm_friend_request():
    _dyn, _db, _friends, _userdata = get_connection(current_app)

    _friends.confirm_pending_request()


@main_bp.route('/delete-friend-request', methods=['POST'])
@login_required
def delete_friend_request():
    _dyn, _db, _friends, _userdata = get_connection(current_app)

    _friends.delete_pending_request()


