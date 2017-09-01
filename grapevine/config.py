"""hierarchical configuration objects"""


class DefaultConfig:
    SECRET_KEY = 'super-secret'
    # JSON_SORT_KEYS = False


class LocalConfig(DefaultConfig):
    """run locally"""
    DEBUG = True
    TESTING = False
    LOCAL_DYNAMO = True


class LocalTestConfig(DefaultConfig):
    """run locally:
    - testing mode
    """
    DEBUG = True
    TESTING = True
    LOCAL_DYNAMO = True


class AWSDevConfig(DefaultConfig):
    """deploy to AWS Staging instance"""
    DEBUG = True
    TESTING = False
    LOCAL_DYNAMO = False


class AWSDevTestConfig(DefaultConfig):
    """deploy to AWS Staging instance:
    - testing mode
    """
    DEBUG = True
    TESTING = True
    LOCAL_DYNAMO = False


class StagingConfig(DefaultConfig):
    """deploy to AWS Staging instance"""
    DEBUG = False
    TESTING = False
    LOCAL_DYNAMO = False


class ProdConfig(DefaultConfig):
    """deploy to AWS Production instance"""
    DEBUG = False
    TESTING = False
    LOCAL_DYNAMO = False
