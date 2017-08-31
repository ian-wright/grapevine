"""hierarchical configuration objects"""


class DefaultConfig:
    SECRET_KEY = 'super-secret'


class LocalConfig(DefaultConfig):
    DEBUG = True
    TESTING = False
    LOCAL_DYNAMO = True


class LocalTestConfig(DefaultConfig):
    DEBUG = True
    TESTING = True
    LOCAL_DYNAMO = True


class AWSDevConfig(DefaultConfig):
    DEBUG = True
    TESTING = False
    LOCAL_DYNAMO = False


class AWSDevTestConfig(DefaultConfig):
    DEBUG = True
    TESTING = True
    LOCAL_DYNAMO = False


class StagingConfig(DefaultConfig):
    DEBUG = False
    TESTING = False
    LOCAL_DYNAMO = False


class ProdConfig(DefaultConfig):
    DEBUG = False
    TESTING = False
    LOCAL_DYNAMO = False
