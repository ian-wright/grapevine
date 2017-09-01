import boto3
from grapevine.dynamo.connection import DynamoResource


# db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
db = DynamoResource().resource

user_table = db.Table('USERS')

# if the table already exists, delete it
try:
    user_table.load()
    user_table.delete()

finally:
    pass


user_table = db.create_table(
    TableName='USERS',
    KeySchema=[
        {
            'AttributeName': 'user_id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'user_id',
            'AttributeType': 'N'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    }
)

# suspend execution until table exists
user_table.meta.client.get_waiter('table_exists').wait(TableName='USERS')

# add a sample record
user_table.put_item(
    Item={
        'user_id': 7,
        'first_name': 'Jane',
        'last_name': 'Doe',
        'age': 25
    }
)

# get that sample record back and print to console
response = user_table.get_item(
    Key={
        'user_id': 7
    }
)
item = response['Item']
print(item)
