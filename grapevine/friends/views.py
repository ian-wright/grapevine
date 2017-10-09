from flask import Blueprint, request, current_app, jsonify
from flask_security.decorators import login_required
from flask_security.core import current_user
from grapevine.utils import get_connection
from validate_email import validate_email

friends_bp = Blueprint('friends_bp', __name__)


@friends_bp.route('/add-friend', methods=['POST'])
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

    # case: Requested user is already one of the current user's friends.
    if target_user and _db.friend_table.get_friendship(current_user.email, target_email):
        user_message = "{} is already in your friend list.".format(target_user.first_name)

    # case: Valid email, GV account exists; send a friend request.
    elif target_user and not _db.friend_table.get_friendship(current_user.email, target_email):
        _friends.send_friend_request(sender_user=current_user, receiver_email=target_email, new_user=False)
        user_message = "We sent {} your connection request.".format(target_user.first_name)

    # case: Valid email, but no account on GV yet; send an app invite w/ special friend request copy.
    #       Upon account confirmation, redirect to the friend accept view.
    elif not target_user and validate_email(target_email):
        _friends.send_friend_request(sender_user=current_user, receiver_email=target_email, new_user=True)
        user_message = "There's no Grapevine account for '{}' yet. \
            We sent an app invite with your connection request.".format(target_email)

    else:
        # case: invalid email address
        user_message = "Please provide a valid email address."

    json_response = jsonify(message=user_message)
    return json_response


@friends_bp.route('/confirm-friend-request', methods=['POST'])
@login_required
def confirm_friend_request():
    _dyn, _db, _friends, _userdata = get_connection(current_app)

    sender_email = request.json['sender_email']
    _friends.confirm_pending_request(current_user.email, sender_email)

    return "Your friendship with {} has been confirmed".format(sender_email)


@friends_bp.route('/delete-friend-request', methods=['POST'])
@login_required
def delete_friend_request():
    _dyn, _db, _friends, _userdata = get_connection(current_app)

    _friends.delete_pending_request()


# @friends_bp.route('/pending-requests', methods=['POST'])
# @login_required
# def list_pending_requests():
