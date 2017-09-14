from flask import Blueprint, render_template, request, redirect, url_for
from flask_security.decorators import anonymous_user_required, login_required
from flask_security.utils import logout_user


main = Blueprint('main', __name__, template_folder='templates')

# TODO - look into enabling token-based authentication with flask-security
@main.route('/', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST' and 'logout' in request.form:
        print('logging user out...')
        logout_user()
        return redirect(url_for('security.login'))

    elif request.method == 'POST' and 'email' in request.form:
        return add_friend(request.form['email'])



    return render_template('main/home.html')


def add_friend(email=None):
    # CASE - email field not valid
    #   flash an invalid message

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

    pass
