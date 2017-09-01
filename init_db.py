
# from grapevine.dynamo.connection import DynamoConn
#
# # get an AWS dynamo connector object
# db = DynamoConn().resource
#
# # # initialize tables
# # tables = {
# #     'user_table': db.Table('USERS')
# # }
# #
# # user_table = db.Table('USERS')
# #
# # for table in tables:
# #     # if the table already exists, delete it
# #     t = tables[table]
# #     try:
# #         t.load()
# #         t.delete()
# #     except:
# #         pass
#
#
# user_table = db.create_table(
#     TableName='USERS',
#     KeySchema=[
#         {
#             'AttributeName': 'user_id',
#             'KeyType': 'HASH'
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'user_id',
#             'AttributeType': 'N'
#         }
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 1,
#         'WriteCapacityUnits': 1
#     }
# )
#
# # suspend execution until table exists
# user_table.meta.client.get_waiter('table_exists').wait(TableName='USERS')
#
# print("created user table")

# # add a sample record
# user_table.put_item(
#     Item={
#         'user_id': 7,
#         'first_name': 'Jane',
#         'last_name': 'Doe',
#         'age': 25
#     }
# )
#
# # get that sample record back and print to console
# response = user_table.get_item(
#     Key={
#         'user_id': 7
#     }
# )
# item = response['Item']
# print(item)

from flask import Flask
from flask_dynamo import Dynamo
from grapevine.auth.views import user_manager
import grapevine.config as cfg

app = Flask(__name__)

# local
# app.config.from_object(cfg.LocalConfig)
# aws dynamo
app.config.from_object(cfg.AWSDevConfig)

with app.app_context():

    # register blueprints
    app.register_blueprint(user_manager, url_prefix='/users')

    # instantiate dynamo extension
    dynamo = Dynamo()
    dynamo.init_app(app)

    # reset schema
    #print("destroying all tables...")
    #dynamo.destroy_all()
    print("creating all tables...")
    dynamo.create_all()
