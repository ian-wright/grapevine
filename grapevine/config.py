"""hierarchical configuration objects"""


class DefaultConfig:
    SECRET_KEY = 'super-secret'
    DYNAMO_TABLES = [
        {
            'TableName': 'USERS',
            'KeySchema': [dict(AttributeName='email', KeyType='HASH')],
            'AttributeDefinitions': [
                dict(AttributeName='email', AttributeType='S')
                # dict(AttributeName='first_name', AttributeType='S'),
                # dict(AttributeName='last_name', AttributeType='S')
            ],
            'ProvisionedThroughput': dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        }, {
            'TableName': 'ARTICLES',
            'KeySchema': [dict(AttributeName='URL', KeyType='HASH')],
            'AttributeDefinitions': [
                dict(AttributeName='URL', AttributeType='S')
                # dict(AttributeName='share_count', AttributeType='N')
            ],
            'ProvisionedThroughput': dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        }
    ]


class LocalConfig(DefaultConfig):
    """run locally"""
    DEBUG = True
    TESTING = False
    # LOCAL_DYNAMO = True
    DYNAMO_ENABLE_LOCAL = True
    DYNAMO_LOCAL_HOST = 'localhost'
    DYNAMO_LOCAL_PORT = 8000


class LocalTestConfig(DefaultConfig):
    """run locally:
    - testing mode
    """
    DEBUG = True
    TESTING = True
    # LOCAL_DYNAMO = True
    DYNAMO_ENABLE_LOCAL = True
    DYNAMO_LOCAL_HOST = 'localhost'
    DYNAMO_LOCAL_PORT = 8000


class AWSDevConfig(DefaultConfig):
    """deploy to AWS Staging instance"""
    DEBUG = True
    TESTING = False
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'


class AWSDevTestConfig(DefaultConfig):
    """deploy to AWS Staging instance:
    - testing mode
    """
    DEBUG = True
    TESTING = True
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'


class StagingConfig(DefaultConfig):
    """deploy to AWS Staging instance"""
    DEBUG = False
    TESTING = False
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'


class ProdConfig(DefaultConfig):
    """deploy to AWS Production instance"""
    DEBUG = False
    TESTING = False
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'
