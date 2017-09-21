

def send_friend_request_existing(sender_email=None, receiver_email=None):
    raise NotImplementedError


def send_app_friend_request(sender_email=None, receiver_email=None):
    raise NotImplementedError


def confirm_friend():
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
