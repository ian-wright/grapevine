
# TODO: write superclass for all db tables


class Users:
    """singleton object is an abstracted representation of database user table"""

    def __init__(self, resource):
        self.table = resource.Table('USERS')

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
