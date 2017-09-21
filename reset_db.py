from flask import Flask
from flask_dynamo import Dynamo
import grapevine.config as cfg


if __name__ == '__main__':

    app = Flask(__name__)

    # local
    app.config.from_object(cfg.LocalConfig)

    # aws dynamo
    # app.config.from_object(cfg.AWSDevConfig)

    with app.app_context():
        # instantiate dynamo extension
        dynamo = Dynamo()
        dynamo.init_app(app)

        # reset schema
        print("destroying all tables...")
        dynamo.create_all()
        dynamo.destroy_all()

        print("creating all tables...")
        dynamo.create_all()
