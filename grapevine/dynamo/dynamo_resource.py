import boto3


class DynamoResource:

    def __init__(self):
        self.resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
