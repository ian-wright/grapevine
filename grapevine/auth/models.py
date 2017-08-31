import random


class User:

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.user_id = random.randint(0, 1000000)
