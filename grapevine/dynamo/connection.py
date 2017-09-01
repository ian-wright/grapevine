import boto3
from grapevine.dynamo.models import Users


class DynamoConn:
    """top-level model to encapsulate a 'connection' to DynamoDB,
     and provide all related models and transactional methods to interface with
     DynamoDB tables
     """

    def __init__(self, local=False):
        if local:
            self.resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            self.resource = boto3.resource('dynamodb', region_name='us-east-1')

        self.user_table = Users(self.resource)



