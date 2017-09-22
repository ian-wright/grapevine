from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from grapevine.dynamo.models import DynamoConn
from werkzeug.local import LocalProxy

# useful instance variables
# flask-dynamo extension
_dynamo = LocalProxy(lambda: current_app.extensions['dynamodb'])
# ORM object
_db = DynamoConn(_dynamo)


def send_friend_request_existing(sender_email=None, receiver_email=None):
    raise NotImplementedError
    # send a custom email encouraging login
    # that's it


def send_app_friend_request(sender_email=None, receiver_email=None):
    raise NotImplementedError
    # send a custom email encouraging registration
    # create a url with an optional param in it, which adds a header to the registration page saying
    # "register to start sharing content with first_name"


def confirm_pending_request():
    raise NotImplementedError
    # add a confirmed_at timestamp to the record in the db
    # send a notification email to the original sender
    # flash a message in the message center
    # write a callback in JS to remove the element from the DOM


def delete_pending_request():
    raise NotImplementedError
    # delete the unconfirmed record from the db
    # send a notification email to the original sender
    # flash a message in the message center
    # write a callback in JS to remove the element from the DOM


def get_pending_requests(email):
    """
    Given the logged in users email id, get a list of {first_name, last_name, email}
    dict objects for each pending friend request.
    :param email: current user's email
    :return: list of dicts, or None if no requests
    """
    raise NotImplementedError


# TODO - should friend invite tokens expire?


class Friendship:

    email_1 = None
    email_2 = None
    requested_at = None
    confirmed_at = None

    def __init__(self, **kwargs):

        email_1 = kwargs.get('email_1')
        email_2 = kwargs.get('email_2')
        hash_key_email, range_key_email = sorted([email_1, email_2])

        self.email_1 = hash_key_email
        self.email_2 = range_key_email
        self.requested_at = kwargs.get('requested_at')
