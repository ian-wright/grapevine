""" All modules related to the application """

from flask import Flask
from grapevine.auth.views import user_manager
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


def create_app(env):
    """ Application factory function """
    if env not in __CFG__:
        raise ValueError("Invalid configuration: %s" % env)

    app = Flask(__name__)
    app.config.from_object(__CFG__[env])

    # register blueprints
    app.register_blueprint(user_manager, url_prefix='/users')

    return app

