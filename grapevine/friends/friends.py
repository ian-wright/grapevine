from flask import current_app, url_for
from flask_security.utils import send_mail, config_value
import datetime


class FriendManager:

    def __init__(self, dynamo_conn):
        self._db = dynamo_conn

    def send_friend_request(self, sender_user=None, receiver_email=None, new_user=False):
        """
        Endpoint to send a new friend request to a specified email. Creates an unconfirmed friendship record
        in the db. Sends a custom email template depending on whether the request recipient is an existing GV
        user or not.
        :param sender_user: email for sender (current user)
        :param receiver_email: email for recipient
        :param new_user: True if recipient is not an existing GV user, False if user account already exists
        :return: friendship object, if all went well
        """
        new_friendship = Friendship(
            sender_email=sender_user.email,
            receiver_email=receiver_email,
            requested_at=datetime.datetime.utcnow()
        )
        self._db.put_model(new_friendship)

        if new_user:
            email_subject = current_app.config['EMAIL_SUBJECT_APP_REQUEST'].format(sender_user.first_name)
            template_string = 'app_request_new_user'
            app_link = url_for('security.register', _external=True)
        else:
            email_subject = current_app.config['EMAIL_SUBJECT_FRIEND_REQUEST'].format(sender_user.first_name)
            template_string = 'friend_request_existing_user'
            app_link =url_for('main_bp.home', _external=True)

        send_mail(
            email_subject,
            receiver_email,
            template_string,
            user=sender_user,
            app_link=app_link
        )
        return new_friendship

    def confirm_pending_request(self, email_1, email_2):
        """
        Given two email addresses representing a friendship, add a confirmed_at date to the friendship object.
        Send a notification email to the original requester.
        :param email_1:
        :param email_2:
        :return: Confirmed friendship object, if successful
        """
        friendship_to_confirm = self._db.friend_table.get_friendship(email_1, email_2)
        friendship_to_confirm.confirmed_at = datetime.datetime.utcnow()
        self._db.put_model(friendship_to_confirm)

        receiver_user = self._db.user_table.get(friendship_to_confirm.receiver_email)

        email_subject = current_app.config['EMAIL_SUBJECT_FRIEND_CONFIRM'].format(receiver_user.first_name)
        template_string = 'friendship_confirmation'
        app_link = url_for('main_bp.home', _external=True)

        # send a notification email to the friendship requester
        send_mail(
            email_subject,
            friendship_to_confirm.sender_email,
            template_string,
            user=receiver_user,
            app_link=app_link
        )
        return friendship_to_confirm

    def delete_pending_request(self, email_1, email_2):
        """
        Given two email addresses representing a friendship, delete the pending friendship object.
        Send a notification email to the original requester.
        :param email_1:
        :param email_2:
        :return: Deleted friendship object, if successful
        """
        deleted_friendship = self._db.friend_table.delete(email_1, email_2)
        receiver_user = self._db.user_table.get(deleted_friendship.receiver_email)

        email_subject = current_app.config['EMAIL_SUBJECT_FRIEND_REJECT'].format(receiver_user.first_name)
        template_string = 'friendship_rejection'

        # send a notification email to the friendship requester
        send_mail(
            email_subject,
            deleted_friendship.sender_email,
            template_string,
            user=receiver_user,
        )
        return deleted_friendship

    def list_pending_requests_users(self, receiver_email):
        """
        Given the logged in users email id, get a list of {first_name, last_name, email}
        dict objects for each pending friend request.
        :param receiver_email: current user's email
        :return: list of dicts, or None if no requests
        """
        requester_emails = self._db.friend_table.list_pending_received_requests(receiver_email)
        return [self._db.user_table.get(email).get_security_payload() for email in requester_emails]


# TODO - should friend invite tokens expire? For now - not using any tokens for friend requests


class Friendship:

    sender_email = None
    receiver_email = None
    requested_at = None
    confirmed_at = None

    def __init__(self, attr_dict=None, **kwargs):
        self.sender_email = kwargs.get('sender_email')
        self.receiver_email = kwargs.get('receiver_email')
        self.requested_at = kwargs.get('requested_at')

    def confirm(self):
        self.confirmed_at = datetime.datetime.utcnow()
        return self


