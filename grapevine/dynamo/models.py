
# TODO: write superclass for all db tables


class Users:
    """abstracted representation of database user table"""

    def __init__(self, underlying_table):
        self.table = underlying_table

    def add(self, new_user):
        try:
            self.table.put_item(
                Item={
                    'email': new_user.email,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name
                }
            )
            return True
        # TODO: what kind of errors thrown here?
        except:
            return False

    def get(self, email):
        user = self.table.get_item(
            Key={
                'email': email
            }
        )
        return user
