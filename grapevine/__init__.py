""" All modules related to the application """

import os
from flask import Flask
from grapevine.auth.views import user_manager


import grapevine.config as cfg
# from interswellar.models import db
# from interswellar.api import bind_api
# from interswellar.views import public_views


__CFG__ = {
    'dev': cfg.DevConfig,
    'devtest': cfg.DevTestConfig,
    'prod': cfg.ProdConfig,
    'prodtest': cfg.ProdTestConfig,
    # 'ci': config.IntegrationConfig,
    # 'ci_test': config.IntegrationConfig
}


def create_app(env):
    """ Application factory function """
    if env not in __CFG__:
        raise ValueError("Invalid configuration: %s" % env)

    app = Flask(__name__)
    app.config.from_object(__CFG__[env])

    # bind_api(app)
    app.register_blueprint(user_manager, url_prefix='/users')



    # with app.app_context():
    #     if app.config['LOCAL_DYNAMO']:
    #         dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    #     else:
    #         dynamodb = boto3.resource('dynamodb')

    return app
