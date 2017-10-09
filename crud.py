
import argparse
import datetime
import json

from flask_security.utils import hash_password

from grapevine import create_app
from grapevine.friends.friends import Friendship
from grapevine.main.views import get_connection

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create or remove DynamoDB objects.')

    parser.add_argument("-m", choices=['loc', 'prod'],
                        help="MODE: DynamoDB instance to access: ( loc | prod ).")
    parser.add_argument("-a", choices=['create', 'delete', 'confirm'],
                        help="ACTION: Create or delete an object: ( create | delete | confirm).")
    parser.add_argument("-c", choices=['user', 'friendship'],
                        help="CLASS: Object type to manipulate: ( user | friendship ).")
    parser.add_argument("params",
                        help="OBJECT PARAMS: json string with object attributes")

    args = vars(parser.parse_args())
    pdict = json.loads(args['params'])

    if args['m'] == 'loc':
        app = create_app('loc')
    else:
        app = create_app('prod')

    with app.app_context():
        _dyn, _db, _friends, _userdata = get_connection(app)

        if args['c'] == 'user':
            if args['a'] == 'create':
                # create new user
                # '{"email":"ian.f.t.wright@gmail.com","password":"password","first_name":"ian","last_name":"wright"}'
                pdict['password'] = hash_password(pdict['password'])
                new_user = _userdata.create_user(**pdict)
                if new_user:
                    print("created new user: {} {}".format(new_user.first_name, new_user.last_name))
                else:
                    print("FAIL: couldn't create new user: {} {}".format(pdict['first_name'], pdict['last_name']))

            elif args['a'] == 'delete':
                # delete user
                # '{"email": "some_email"}'
                if _db.user_table.delete(pdict['email']):
                    print("deleted user: {}".format(pdict['email']))
                else:
                    print("FAIL: couldn't delete user: {}".format(pdict['email']))

            elif args['a'] == 'confirm':
                # confirm new user
                # '{"email": "some_email"}'
                user_to_confirm = _userdata.get_user(pdict['email'])
                user_to_confirm.confirmed_at = datetime.datetime.utcnow()
                if _userdata.put(user_to_confirm):
                    print("confirmed user: {}".format(pdict['email']))
                else:
                    print("FAIL: couldn't confirm user: {}".format(pdict['email']))

        elif args['c'] == 'friendship':
            if args['a'] == 'create':
                # create friendship
                # '{"sender_email":"mike@gmail.com","receiver_email":"bill@gmail.com"}'
                pdict["requested_at"] = datetime.datetime.utcnow()
                new_friendship = Friendship(**pdict)
                if _db.put_model(new_friendship):
                    print("created new friendship: {} + {}".format(pdict['sender_email'], pdict['receiver_email']))
                else:
                    print("FAIL: couldn't create new friendship: {} + {}"\
                          .format(pdict['sender_email'], pdict['receiver_email']))

            elif args['a'] == 'delete':
                # delete friendship
                # '{"email_1":"mike@gmail.com","email_2":"bill@gmail.com"}'
                if _db.friend_table.delete(pdict['email_1'], pdict['email_2']):
                    print("deleted friendship: {} + {}".format(pdict['email_1'], pdict['email_2']))
                else:
                    print("couldn't delete friendship: {} + {}".format(pdict['email_1'], pdict['email_2']))

            elif args['a'] == 'confirm':
                # confirm friendship
                # '{"email_1":"mike@gmail.com","email_2":"bill@gmail.com"}'
                if _friends.confirm_pending_request(pdict['email_1'], pdict['email_2']):
                    print("confirmed friendship: {} + {}".format(pdict['email_1'], pdict['email_2']))
                else:
                    print("couldn't confirm friendship: {} + {}".format(pdict['email_1'], pdict['email_2']))
