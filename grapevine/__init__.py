
# TODO: integrate TravisCI

import grapevine.config as cfg
from flask import Flask, send_from_directory
from flask_cors import CORS
from grapevine.dynamo.orm import DynamoConn
from grapevine.security.models import User, Role, DynamoUserDatastore
from grapevine.main.forms import RegisterFormWithNames, ConfirmRegisterFormWithNames
from grapevine.main.views import main_bp
from grapevine.friends.views import friends_bp
import os


def create_app(env):
    from grapevine.extension_models import mail, security, dynamo

    __CFG__ = {
        'loc': cfg.LocalConfig,
        'loctest': cfg.LocalTestConfig,
        'awsdev': cfg.AWSDevConfig,
        'awsdevtest': cfg.AWSDevTestConfig,
        'stage': cfg.StagingConfig,
        'prod': cfg.ProdConfig
    }
    if env not in __CFG__:
        raise ValueError("Invalid configuration: %s" % env)

    app = Flask(__name__)
    app.config.from_object(__CFG__[env])

    # initialize flask-mail
    mail.init_app(app)

    # require an app context to initialize the dynamo extension
    with app.app_context():
        dynamo.init_app(app)

    # instantiate an abstract dynamo connector that sits on top of base-level dynamo extension object
    db = DynamoConn(dynamo)
    user_datastore = DynamoUserDatastore(db, User, Role)
    security.init_app(
        app,
        user_datastore,
        register_form=RegisterFormWithNames,
        confirm_register_form=ConfirmRegisterFormWithNames
    )

    # register blueprints
    # (flask-security blueprint is registered at extension initialization)
    app.register_blueprint(main_bp)
    app.register_blueprint(friends_bp)

    # serve the React app assets
    # @app.route('/', defaults={'path': ''})
    # @app.route('/<path:path>')
    # def react(path):
    #     if path == "":
    #         return send_from_directory('react-build', 'index.html')
    #     # that go from the post-confirm pages back to S3
    #     else:
    #         if os.path.exists('./grapevine/react-build/' + path):
    #             return send_from_directory('react-build', path)
    #         else:
    #             print("catching a path...")
    #             return send_from_directory('react-build', 'index.html')

    # log all available endpoints
    # print("\nAVAILABLE RULES:\n")
    # for rule in app.url_map.iter_rules():
    #     print("url:", rule)
    #     print("endpoint:", rule.endpoint, "\n")

    # enable cross-domain API requests
    # TODO - may need to enable cross-domain cookies if I ever use sessions... but do I?
    CORS(app)

    return app

