from flask_dynamo import Dynamo
from flask_security import Security
from flask_mail import Mail

"""instantiating extension objects in separate scope to avoid binding
to any one instance of an app
"""
dynamo = Dynamo()
security = Security()
mail = Mail()
