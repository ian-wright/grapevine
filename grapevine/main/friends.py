from flask import current_app, url_for
# from grapevine.dynamo.models import DynamoConn
from flask_security.utils import send_mail, config_value
from werkzeug.local import LocalProxy
import datetime

# useful instance variables
# flask-dynamo extension
# _dynamo = LocalProxy(lambda: current_app.extensions['dynamodb'])
# ORM object
# _db = DynamoConn(_dynamo)


# def send_mail(subject, recipient, template, **context):
#     """Send an email via the Flask-Mail extension.
#
#     :param subject: Email subject
#     :param recipient: Email recipient
#     :param template: The name of the email template
#     :param context: The context to render the template with
#     """
#
#     context.setdefault('security', _security)
#     context.update(_security._run_ctx_processor('mail'))
#
#     msg = Message(subject,
#                   sender=_security.email_sender,
#                   recipients=[recipient])
#
#     ctx = ('security/email', template)
#     if config_value('EMAIL_PLAINTEXT'):
#         msg.body = render_template('%s/%s.txt' % ctx, **context)
#     if config_value('EMAIL_HTML'):
#         msg.html = render_template('%s/%s.html' % ctx, **context)
#
#     if _security._send_mail_task:
#         _security._send_mail_task(msg)
#         return
#
#     mail = current_app.extensions.get('mail')
#     mail.send(msg)

class FriendManager:

    def __init__(self, dynamo_conn):
        self._db = dynamo_conn

    def send_friend_request_existing(self, sender_user=None, receiver_email=None):
        # create a new unconfirmed friendship object, write to db
        # send a custom email encouraging login
        # link is just to normal login
        # that's it

        new_friendship = Friendship(
            sender_email=sender_user.email,
            receiver_email=receiver_email,
            requested_at=datetime.datetime.utcnow()
        )
        self._db.put_model(new_friendship)

        email_subject = config_value('EMAIL_SUBJECT_FRIEND_REQUEST')
        print('email sub:', email_subject)
        email_subject = email_subject.format(sender_user.first_name)
        print('email sub:', email_subject)
        send_mail(
            email_subject,
            receiver_email,
            'friend_request_existing_user',
            user=sender_user,
            confirmation_link=url_for('main_bp.home')
        )
        return True

    def send_app_friend_request(self, sender_user=None, receiver_email=None):
        raise NotImplementedError
        # send a custom email encouraging registration
        # create a url with an optional param in it, which adds a header to the registration page saying
        # "register to start sharing content with first_name"

    def confirm_pending_request(self, email_1, email_2):
        friendship_to_confirm = self._db.friend_table.get_friendship(email_1, email_2)
        print("friendship_to_confirm", vars(friendship_to_confirm))
        return self._db.put_model(friendship_to_confirm.confirm())

        # TODO:
        # add a confirmed_at timestamp to the record in the db
        # send a notification email to the original sender
        # flash a message in the message center
        # write a callback in JS to remove the element from the DOM

    def delete_pending_request(self):
        raise NotImplementedError
        # delete the unconfirmed record from the db
        # send a notification email to the original sender
        # flash a message in the message center
        # write a callback in JS to remove the element from the DOM

    def list_pending_requests(self, email):
        """
        Given the logged in users email id, get a list of {first_name, last_name, email}
        dict objects for each pending friend request.
        :param email: current user's email
        :return: list of dicts, or None if no requests
        """
        # TODO - awkward to have such heavy functionality on the ORM side... could move methods to this manager
        return self._db.friend_table.list_pending_received_requests(email)


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


