from flask_security.datastore import Datastore, UserDatastore
import boto3


class DynamoDatastore(Datastore):
    """
    """
    def __init__(self, local=False):
        if local:
            db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            db = boto3.resource('dynamodb', region_name='us-east-1')
        super(DynamoDatastore, self).__init__(db)

    def put(self, model):
        # add a table to dynamo
        self.db.session.add(model)
        return model

    def delete(self, model):
        # delete a table to dynamo
        self.db.session.delete(model)


class DynamoUserDatastore(DynamoDatastore, UserDatastore):
    """
    """
    def __init__(self, db, user_model, role_model):
        MongoEngineDatastore.__init__(self, db)
        UserDatastore.__init__(self, user_model, role_model)

    def get_user(self, identifier):
        from mongoengine import ValidationError
        try:
            return self.user_model.objects(id=identifier).first()
        except (ValidationError, ValueError):
            pass
        for attr in get_identity_attributes():
            query_key = '%s__iexact' % attr
            query = {query_key: identifier}
            rv = self.user_model.objects(**query).first()
            if rv is not None:
                return rv

    def find_user(self, **kwargs):
        try:
            from mongoengine.queryset import Q, QCombination
        except ImportError:
            from mongoengine.queryset.visitor import Q, QCombination
        from mongoengine.errors import ValidationError

        queries = map(lambda i: Q(**{i[0]: i[1]}), kwargs.items())
        query = QCombination(QCombination.AND, queries)
        try:
            return self.user_model.objects(query).first()
        except ValidationError:  # pragma: no cover
            return None

    def find_role(self, role):
        return self.role_model.objects(name=role).first()