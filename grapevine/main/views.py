from flask import Blueprint, send_from_directory, render_template, request, redirect, url_for, current_app, jsonify
from flask_security.decorators import login_required, auth_token_required
from flask_security.utils import logout_user, hash_password
from flask_security.core import current_user
from grapevine.utils import get_connection
import datetime
import os


main_bp = Blueprint('main_bp', __name__)


@main_bp.before_app_first_request
def before_first_request():

    with current_app.app_context():
        _dyn, _db, _friends, _userdata = get_connection(current_app)

        # Create any database tables that don't exist yet.
        _dyn.create_all()

        # Create the admin role (royal) and end-user role (pleb), unless they already exist
        _userdata.find_or_create_role(name='royal', description='administrator')
        _userdata.find_or_create_role(name='pleb', description='end user')

        # Create two Users for testing purposes, unless they already exist.
        encrypted_password = hash_password('password')
        if not _userdata.get_user('ian.f.t.wright@gmail.com'):
            _userdata.create_user(
                email='ian.f.t.wright@gmail.com',
                password=encrypted_password,
                first_name='Ian-Admin',
                last_name='Wright',
                confirmed_at=datetime.datetime.utcnow()
            )
        if not _userdata.get_user('iw453@nyu.edu'):
            _userdata.create_user(
                email='iw453@nyu.edu',
                password=encrypted_password,
                first_name='Ian-User',
                last_name='Wright',
                confirmed_at=datetime.datetime.utcnow()
            )

        # assign roles to users, if they're not already assigned
        _userdata.add_role_to_user('iw453@nyu.edu', 'pleb')
        _userdata.add_role_to_user('ian.f.t.wright@gmail.com', 'royal')


# @main_bp.route('/')
# def react-build():
#     return render_template('index.html')


# @main_bp.route('/validate-token', methods=['GET', 'OPTIONS'])
@main_bp.route('/validate-token')
@auth_token_required
def validate_token():
    """
    Because this view is token-protected, it only returns a 200 if a valid token exists on client side.
    :return: status 401 if unauthorized (invalid token), 200 if authorized (valid token)
    """
    return jsonify(data="ok")

