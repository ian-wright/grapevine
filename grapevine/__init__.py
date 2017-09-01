""" All modules related to the application """

import os
from flask import Flask
from flask import g
from grapevine.auth.views import user_manager
from grapevine.dynamo.connection import DynamoConn
import grapevine.config as cfg


# TODO: integrate TravisCI configurations
__CFG__ = {
    'loc': cfg.LocalConfig,
    'loctest': cfg.LocalTestConfig,
    'awsdev': cfg.AWSDevConfig,
    'awsdevtest': cfg.AWSDevTestConfig,
    'stage': cfg.StagingConfig,
    'prod': cfg.ProdConfig
}

db = None

def create_app(env):
    """ Application factory function """
    if env not in __CFG__:
        raise ValueError("Invalid configuration: %s" % env)

    app = Flask(__name__)
    app.config.from_object(__CFG__[env])


    # if app.config['LOCAL_DYNAMO']:
    #     db = DynamoConn(local=True)
    # else:
    #     db = DynamoConn()

    # bind_api(app)
    # register blueprints
    app.register_blueprint(user_manager, url_prefix='/users')

    # this may not need to be enclosed with the app context - is it good practice?
    # with app.app_context():
    #     if app.config['LOCAL_DYNAMO']:
    #         db = DynamoConn(local=True)
    #     else:
    #         db = DynamoConn()

    return app

