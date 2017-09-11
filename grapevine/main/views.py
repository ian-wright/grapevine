from flask import Blueprint, render_template, request, redirect, url_for
from flask_security.decorators import anonymous_user_required, login_required
from flask_security.core import current_user
from flask_security.utils import logout_user

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST':
        print('logging user out...')
        logout_user()
        print('redirect to login page...')
        return redirect(url_for('security.login'))


    return render_template('main/home.html', current_user=current_user)
