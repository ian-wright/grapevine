from grapevine.dynamo.dynamo_resource import DynamoResource


class Users:
    """acts as singleton object to interface with DynamoDB user table"""

    def __init__(self):
        self.table = DynamoResource().resource.Table('USERS')

    def add(self, new_user):
        try:
            self.table.put_item(
                Item={
                    'user_id': new_user.user_id,
                    'name': new_user.name,
                    'email': new_user.email
                }
            )
            return True
        except:
            return False

    def get(self, user_id):
        user = self.table.get_item(
            Key={
                'user_id': user_id
            }
        )
        return user
