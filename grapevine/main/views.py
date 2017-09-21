from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_security.decorators import login_required
from flask_security.utils import logout_user, hash_password
from flask_security.core import current_user
from werkzeug.local import LocalProxy
# from grapevine.main.friends import add_friend
# from grapevine.main.forms import InviteEmailForm, InviteUserEmailForm

from validate_email import validate_email

_dynamo = LocalProxy(lambda: current_app.extensions['dynamodb'])
_security = LocalProxy(lambda: current_app.extensions['security'])
_datastore = LocalProxy(lambda: _security.datastore)

main = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')


@main.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    with current_app.app_context():
        _dynamo.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    _datastore.find_or_create_role(id=0, name='royal', description='administrator')
    _datastore.find_or_create_role(id=1, name='pleb', description='end user')

    # Create two Users for testing purposes -- unless they already exist.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = hash_password('password')
    if not _datastore.get_user('ian.f.t.wright@gmail.com'):
        _datastore.create_user(
            email='ian.f.t.wright@gmail.com',
            password=encrypted_password,
            first_name='Ian-Admin',
            last_name='Wright'
        )
    if not _datastore.get_user('iw453@nyu.edu'):
        _datastore.create_user(
            email='iw453@nyu.edu',
            password=encrypted_password,
            first_name='Ian-User',
            last_name='Wright'
        )

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    _datastore.add_role_to_user('iw453@nyu.edu', 'pleb')
    _datastore.add_role_to_user('ian.f.t.wright@gmail.com', 'royal')


# TODO - look into enabling token-based authentication with flask-security
@main.route('/', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST' and 'logout' in request.form:
        print('logging user out...')
        logout_user()
        return redirect(url_for('security.login'))

    return render_template('main/home.html')


@main.route('/add-friend', methods=['POST'])
@login_required
def add_friend():
    """
    Takes an email address as JSON from a client-side ajax post request, validates the email,
    and either:
        - asks for a valid email (if necessary)
        - sees an existing GV user with the requested email and sends a friend request email
        - determines that the requested email isn't yet in the db, and sends an invite email to the new user.
    The server will instantiate a WTForm object for validation
    :return: feedback message to client for immediate display beside form
    """
    target_email = request.json['email']
    target_user = _datastore.get_user(target_email)
    if target_user and target_user.email in current_user.friends:
        # case: Requested user is already one of the current user's friends.
        user_message = "{} is already in your friend list.".format(target_user.first_name)

    elif target_user and target_user.email not in current_user.friends:
        # case: Valid email, GV account exists; send a friend request.
        user_message = "We'll send {} your connection request.".format(target_user.first_name)

    elif not target_user and validate_email(target_email):
        # case: Valid email, but no account on GV yet; send an app invite w/ special friend request copy.
        #       Upon account confirmation, redirect to the friend accept view.
        user_message = "There's no Grapevine account for {} yet. \
            We'll send an app invite and your connection request.".format(target_email)

    else:
        # case: invalid email address
        user_message = "Please provide a valid email address."

    return user_message



