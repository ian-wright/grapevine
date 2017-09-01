""" All modules related to the application """

from flask import Flask
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
    from grapevine.auth.views import user_manager
    app.register_blueprint(user_manager, url_prefix='/users')

    with app.app_context():
        # instantiate dynamo object
        from grapevine.dynamo_model import dynamo
        dynamo.init_app(app)

    return app

