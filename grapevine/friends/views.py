from flask import Blueprint, request, current_app, jsonify, make_response
from flask_security.decorators import auth_token_required
from flask_security.core import current_user
from grapevine.utils import get_connection
from validate_email import validate_email

friends_bp = Blueprint('friends_bp', __name__)


@friends_bp.route('/add-friend', methods=['POST'])
@auth_token_required
def add_friend():
    """
    Takes an email address as JSON from a client-side ajax post request, validates the email,
    and either:
        - asks for a valid email (if necessary)
        - sees that the requested user is already a friend of the current user
        - sees an existing GV user with the requested email and sends a friend request email
        - determines that the requested email isn't yet in the db, and sends an app invite email to the new user.
    :return:
    response = {
        'valid_email': 'false' | 'true',
        'existing_friend': 'false' | {
            'first_name': 'Bill',
            'last_name': 'Smith',
            'email': 'bill.smith@fake.com'
        },
        'existing_user': 'false' | {
            'first_name': 'Bill',
            'last_name': 'Smith',
            'email': 'bill.smith@fake.com'
            'sent_request': 'true | 'false'
        },
        'new_user': 'false' | {
            'email': 'bill.smith@fake.com'
            'sent_request': 'true | 'false'
        }
    }
    """
    conn = get_connection(current_app)
    _db = conn['_db']
    _users = conn['_users']
    _friends = conn['_friends']

    target_email = request.json['target_email']
    target_user = _users.get_user(target_email)

    response = {
        'valid_email': 'false',
        'existing_friend': 'false',
        'existing_user': 'false',
        'new_user': 'false'
    }

    # case: Requested user is already one of the current user's friends.
    if target_user and _db.friend_table.get_friendship(current_user.email, target_email):
        response['valid_email'] = 'true'
        response['existing_friend'] = {
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_email
        }
        # status - OK
        status = 200

    # case: Valid email, GV account exists; send a friend request.
    elif target_user and not _db.friend_table.get_friendship(current_user.email, target_email):
        did_send = _friends.send_friend_request(
            sender_user=current_user,
            receiver_email=target_email,
            new_user=False
        )
        response['valid_email'] = 'true'
        response['existing_user'] = {
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_email,
            'sent_request': 'true' if did_send else 'false'
        }
        # status - CREATED
        status = 201

    # case: Valid email, but no account on GV yet; send an app invite w/ special friend request copy.
    #       Upon account confirmation, redirect to the friend accept view.
    elif not target_user and validate_email(target_email):
        did_send = _friends.send_friend_request(sender_user=current_user, receiver_email=target_email, new_user=True)
        response['valid_email'] = 'true'
        response['new_user'] = {
            'email': target_email,
            'sent_request': 'true' if did_send else 'false'
        }
        # status - CREATED
        status = 201

    else:
        # case: invalid email address
        # status - BAD REQUEST
        status = 400

    return make_response(jsonify(response), status)


@friends_bp.route('/confirm-friend-request', methods=['POST'])
@auth_token_required
def confirm_friend_request():
    """
    Confirms a pending friend request, and sends a confirmation email to original requester
    :return: {'confirmed': 'true' | 'false}
    """
    conn = get_connection(current_app)
    _friends = conn['_friends']

    requester_email = request.json['requester_email']
    did_confirm = _friends.confirm_pending_request(current_user.email, requester_email)

    response = {'confirmed': 'true' if did_confirm else 'false'}
    status = 200 if did_confirm else 400
    return make_response(jsonify(response), status)


@friends_bp.route('/delete-friend-request', methods=['POST'])
@auth_token_required
def delete_friend_request():
    """
    Deletes a pending friend request, and sends a rejection email to original requester
    :return: {'deleted': 'true' | 'false}
    """
    conn = get_connection(current_app)
    _friends = conn['_friends']

    requester_email = request.json['requester_email']
    did_delete = _friends.delete_pending_request(current_user.email, requester_email)

    response = {'deleted': 'true' if did_delete else 'false'}
    status = 200 if did_delete else 400
    return make_response(jsonify(response), status)


@friends_bp.route('/list-pending-requests', methods=['POST'])
@auth_token_required
def list_pending_requests():
    """

    :return:
    """
    pass


@friends_bp.route('/list-confirmed-friends', methods=['POST'])
@auth_token_required
def list_confirmed_friends():
    """

    :return:
    """
    pass
