from flask import Blueprint, request, current_app, jsonify, make_response
from flask_security.decorators import auth_token_required
from flask_security.core import current_user
from grapevine.utils import get_connection

shares_bp = Blueprint('shares_bp', __name__)


@shares_bp.route('/send-share', methods=['POST'])
@auth_token_required
def send_share():
    """

    :return:
    """
    conn = get_connection(current_app)
    _shares = conn['_shares']
    _db = conn['_db']

    receiver_emails = request.json['receiver_emails']
    url = request.json['url']
    sender_email = current_user.email

    success = True
    for receiver_email in receiver_emails:
        # check that email pair is a valid Friendship
        if _db.friend_table.get_friendship(sender_email, receiver_email):
            sent_share = _shares.generate_share(
                sender_email=sender_email,
                receiver_email=receiver_email,
                url=url
            )
            if not sent_share:
                success = False
        else:
            success = False

    response = {'sent': 'true' if success else 'false'}
    status = 200 if success else 400
    return make_response(jsonify(response), status)


@shares_bp.route('/list-shares', methods=['POST'])
@auth_token_required
def list_shares():
    """

    :return:
    """
    conn = get_connection(current_app)
    _shares = conn['_shares']

    sender_email = request.json['friend_email']
    receiver_email = current_user.email

    _shares.list_shares_with_articles(
        sender_email=sender_email,
        receiver_email=receiver_email
    )