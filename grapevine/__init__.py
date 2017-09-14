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

    from grapevine.extension_models import mail, security
    mail.init_app(app)

    # require an app context to initialize the dynamo extension
    with app.app_context():
        from grapevine.extension_models import dynamo
        dynamo.init_app(app)

    # instantiate an abstract dynamo connector that sits on top of base extension object
    from grapevine.dynamo.models import DynamoConn
    from grapevine.security.models import User, Role, DynamoUserDatastore
    from grapevine.form_override import RegisterFormWithNames, ConfirmRegisterFormWithNames
    db = DynamoConn(dynamo)
    user_datastore = DynamoUserDatastore(db, User, Role)
    security.init_app(
        app,
        user_datastore,
        register_form=RegisterFormWithNames,
        confirm_register_form=ConfirmRegisterFormWithNames
    )

    # register blueprints
    # flask-security blueprint is registered upon initialization
    from grapevine.main.views import main
    app.register_blueprint(main)

    # TEMP TEST
    # print("\nAVAILABLE RULES:\n")
    # for rule in app.url_map.iter_rules():
    #     print("url:", rule)
    #     print("endpoint:", rule.endpoint, "\n")

    return app

