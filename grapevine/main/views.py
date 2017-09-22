from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_security.decorators import login_required
from flask_security.utils import logout_user, hash_password
from flask_security.core import current_user
from werkzeug.local import LocalProxy
from grapevine.dynamo.models import DynamoConn
from grapevine.main.friends import send_friend_request_existing, send_app_friend_request, get_pending_requests, \
    Friendship, confirm_pending_request, delete_pending_request
# from grapevine.main.forms import InviteEmailForm, InviteUserEmailForm

import datetime

from validate_email import validate_email

# useful instance variables
# flask-dynamo extension
_dynamo = LocalProxy(lambda: current_app.extensions['dynamodb'])
# ORM object
_db = DynamoConn(_dynamo)
# flask-security extension
_security = LocalProxy(lambda: current_app.extensions['security'])
# user_datastore required for flask-security
_user_datastore = LocalProxy(lambda: _security.datastore)

main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')


@main_bp.before_app_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    with current_app.app_context():
        _dynamo.create_all()

    # Create the admin role (royal) and end-user role (pleb), unless they already exist
    _user_datastore.find_or_create_role(id=0, name='royal', description='administrator')
    _user_datastore.find_or_create_role(id=1, name='pleb', description='end user')

    # Create two Users for testing purposes, unless they already exist.
    encrypted_password = hash_password('password')
    if not _user_datastore.get_user('ian.f.t.wright@gmail.com'):
        _user_datastore.create_user(
            email='ian.f.t.wright@gmail.com',
            password=encrypted_password,
            first_name='Ian-Admin',
            last_name='Wright'
        )
    if not _user_datastore.get_user('iw453@nyu.edu'):
        _user_datastore.create_user(
            email='iw453@nyu.edu',
            password=encrypted_password,
            first_name='Ian-User',
            last_name='Wright'
        )

    # assign roles to users, if they're not already assigned
    _user_datastore.add_role_to_user('iw453@nyu.edu', 'pleb')
    _user_datastore.add_role_to_user('ian.f.t.wright@gmail.com', 'royal')


# TODO - look into enabling token-based authentication with flask-security
@main_bp.route('/', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST' and 'logout' in request.form:
        print('logging user out...')
        logout_user()
        return redirect(url_for('security.login'))

    pending_friends = get_pending_requests(current_user.email)
    return render_template('main/home.html', pending_friends=pending_friends)


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
    target_email = request.json['email']
    target_user = _user_datastore.get_user(target_email)

    # TODO - change current_user.friends to the friends table method calls
    if target_user and _db.friend_table.is_friend(current_user.email, target_email):
        # case: Requested user is already one of the current user's friends.
        user_message = "{} is already in your friend list.".format(target_user.first_name)

    elif target_user and not _db.friend_table.is_friend(current_user.email, target_email):
        # case: Valid email, GV account exists; send a friend request.
        send_friend_request_existing(sender_email=current_user.email, receiver_email=target_email)
        new_friendship = Friendship(
            email_1=current_user.email,
            email_2=target_email,
            requested_at=datetime.datetime.utcnow(),
            confirmed_at=None
        )
        _db.put_model(new_friendship)
        user_message = "We sent {} your connection request.".format(target_user.first_name)

    elif not target_user and validate_email(target_email):
        # case: Valid email, but no account on GV yet; send an app invite w/ special friend request copy.
        #       Upon account confirmation, redirect to the friend accept view.
        send_app_friend_request(sender_email=current_user.email, receiver_email=target_email)
        new_friendship = Friendship(
            email_1=current_user.email,
            email_2=target_email,
            requested_at=datetime.datetime.utcnow(),
            confirmed_at=None
        )
        _db.put_model(new_friendship)
        user_message = "There's no Grapevine account for {} yet. \
            We sent an app invite with your connection request.".format(target_email)

    else:
        # case: invalid email address
        user_message = "Please provide a valid email address."

    return user_message


@main_bp.route('/confirm-friend-request', methods=['POST'])
@login_required
def confirm_friend_request():
    confirm_pending_request()


@main_bp.route('/delete-friend-request', methods=['POST'])
@login_required
def delete_friend_request():
    delete_pending_request()


