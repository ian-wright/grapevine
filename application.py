""" required app entry point for AWS EB environment """

import os
from grapevine import create_app

application = create_app(os.environ.get('APP_ENV', 'loc'))

print("server root:", application.root_path)

if __name__ == "__main__":
    application.run()
