from flask import request, flash, render_template
from grapevine.main.forms import InviteEmailForm, InviteUserEmailForm


def add_friend(email):
    form = InviteUserEmailForm(**request.form)
    if form.validate():
        print('valid existing user')
        flash('this is an existing grapevine user')
        # send friend invite email
    else:
        form = InviteEmailForm(request.form)
        if form.validate():
            print('new user; valid email')
            flash('this is valid email')
            # send grapevine invite email
        else:
            flash('please provide a valid email address.')
            # do nothing
    return render_template('main/home.html')

    # CASE - email valid, already in friend list
    #   flash an already friend message

    # CASE - email valid, not a friend, but already in grapevine
    #   generate a unique URL to confirm
    #   send the friend confirmation email
    #   add a "pending" friend to the sender's friend set ('confirmed' datestamp is None)
    #   upon confirming:
    #       redirect receiving user to their home page, but flash a messsage
    #       update both users friends lists with emails and confirmation datestamps
    #
    # CASE - email valid, invite to grapevine
    # message flashing to frontend:
    #   already in friend list
    #   sent grapevine invite to person
    #   sent friend invite (friend already has a


class Friendship:
    email_1 = None
    email_2 = None
    requested_at = None
    confirmed_at = None

    def __init__(self, **kwargs):
        self.email_1 = kwargs.get('email_1')
        self.email_2 = kwargs.get('email_2')
        self.confirmed_at = kwargs.get('confirmed_at')
