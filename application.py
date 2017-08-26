from flask import Flask
import boto3

application = Flask(__name__)


@application.route('/')
def hello_world():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    user_table = dynamodb.Table('USERS')

    user_table.put_item(
        Item={
            'user_id': '2',
            'first_name': 'Joe',
            'last_name': 'Smith',
            'age': 15
        }
    )

    response = user_table.get_item(
        Key={
            'user_id': '2'
        }
    )
    print(response)
    item = response['Item']
    print(str(item))
    return 'Hello World!' + str(item)


if __name__ == '__main__':
    application.debug = True
    application.run()
