"""hierarchical configuration objects"""


class DefaultConfig:
    # TODO: store an actual secret and random key in an env var
    SECRET_KEY = 'super-secret'
    DYNAMO_TABLES = [
        {
            'TableName': 'USERS',
            'KeySchema': [dict(AttributeName='email', KeyType='HASH')],
            'AttributeDefinitions': [dict(AttributeName='email', AttributeType='S')],
            'ProvisionedThroughput': dict(ReadCapacityUnits=2, WriteCapacityUnits=2)
        },
        {
            'TableName': 'ROLES',
            'KeySchema': [dict(AttributeName='id', KeyType='HASH')],
            'AttributeDefinitions': [dict(AttributeName='id', AttributeType='N')],
            'ProvisionedThroughput': dict(ReadCapacityUnits=2, WriteCapacityUnits=2)
        },
        {
            'TableName': 'FRIENDS',
            'KeySchema': [dict(AttributeName='email_1', KeyType='HASH')],
            'GlobalSecondaryIndexes': [dict(IndexName='email_2',
                                            KeySchema=[dict(AttributeName='email_2', KeyType='HASH')],
                                            Projection=dict(ProjectionType='ALL'),
                                            ProvisionedThroughput=dict(ReadCapacityUnits=2, WriteCapacityUnits=2))],
            'AttributeDefinitions': [dict(AttributeName='email_1', AttributeType='S'),
                                     dict(AttributeName='email_2', AttributeType='S')],
            'ProvisionedThroughput': dict(ReadCapacityUnits=2, WriteCapacityUnits=2)
        },
        {
            'TableName': 'ARTICLES',
            'KeySchema': [
                dict(AttributeName='domain', KeyType='HASH'),
                dict(AttributeName='id', KeyType='RANGE')
            ],
            # TODO: read about proper range key usage (good for article table?)
            'AttributeDefinitions': [
                dict(AttributeName='domain', AttributeType='S'),
                dict(AttributeName='id', AttributeType='S')
            ],
            'ProvisionedThroughput': dict(ReadCapacityUnits=2, WriteCapacityUnits=2)
        }
    ]
    # flask-security config settings
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    # TODO: store an actual salt and random key in an env var
    SECURITY_PASSWORD_SALT = 'another-super-secret'
    SECURITY_CONFIRM_URL = '/account-confirm'
    SECURITY_EMAIL_SUBJECT_CONFIRM = "Confirm your email to join Grapevine"

    # custom endpoint for friend invite confirmation
    FRIEND_CONFIRM_URL = '/friend-confirm'
    FRIEND_EMAIL_SUBJECT_CONFIRM = "{} wants to connect on Grapevine"

    # flask-mail config settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'ian.f.t.wright@gmail.com'
    MAIL_PASSWORD = 'xcjhwfhrwedwquay' # provided by google for app-specific access
    SECURITY_EMAIL_SENDER = 'ian.f.t.wright@gmail.com'


class LocalConfig(DefaultConfig):
    """loc: run locally"""
    FLASK_DEBUG = True
    TESTING = False
    # LOCAL_DYNAMO = True
    DYNAMO_ENABLE_LOCAL = True
    DYNAMO_LOCAL_HOST = 'localhost'
    DYNAMO_LOCAL_PORT = 8000


class LocalTestConfig(DefaultConfig):
    """loctest: run locally:
    - testing mode
    """
    FLASK_DEBUG = True
    TESTING = True
    # LOCAL_DYNAMO = True
    DYNAMO_ENABLE_LOCAL = True
    DYNAMO_LOCAL_HOST = 'localhost'
    DYNAMO_LOCAL_PORT = 8000


class AWSDevConfig(DefaultConfig):
    """awsdev: deploy to AWS Staging instance"""
    FLASK_DEBUG = True
    TESTING = False
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'


class AWSDevTestConfig(DefaultConfig):
    """awsdevtest: deploy to AWS Staging instance:
    - testing mode
    """
    FLASK_DEBUG = True
    TESTING = True
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'


class StagingConfig(DefaultConfig):
    """stage: deploy to AWS Staging instance"""
    FLASK_DEBUG = False
    TESTING = False
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'


class ProdConfig(DefaultConfig):
    """prod: deploy to AWS Production instance"""
    FLASK_DEBUG = False
    TESTING = False
    # LOCAL_DYNAMO = False
    DYNAMO_ENABLE_LOCAL = False
    AWS_REGION = 'us-east-1'
