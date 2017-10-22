import pytest
import datetime
from grapevine import create_app
from grapevine.utils import get_connection
from grapevine.security.models import User, Role
from grapevine.friends.friends import Friendship, FriendManager
from grapevine.shares.shares import Article, Share


# 'request' in this context is a request that Pytest makes within a test function for a required fixture
@pytest.fixture(scope='class')
def gv_conns(request):
    # setup code
    app = create_app('loctest')
    conn = get_connection(app)
    conn['_dyn'].create_all()

    # inject instance variables into test classes
    request.cls.app = app
    request.cls._dyn = conn['_dyn']
    request.cls._db = conn['_db']
    request.cls._users = conn['_users']
    request.cls._friends = conn['_friends']
    request.cls._shares = conn['_shares']
    yield

    # teardown code
    conn['_dyn'].destroy_all()


@pytest.mark.usefixtures('gv_conns')
class TestUserModels:

    def test_create_retrieve_user(self):
        """
        PROCEDURE:
        - create a test user object
        - write it to db
        - retrieve from db
        - assert that retrieved instance matches original
        - assert that retrieved obj is of User type

        UNIQUE COVERAGE:
        - flask-security create_user()
        - ORM put_model()
        - BaseTable add()
        - UserTable put_item()
        - flask-security get_user()
        - UserTable get()
        - ORM response_to_object()
        - User class
        """
        with self.app.app_context():
            in_user = self._users.create_user(
                email='ian.f.t.wright+1@gmail.com',
                password='password1',
                first_name='ian1',
                last_name='wright'
            )
            out_user = self._users.get_user('ian.f.t.wright+1@gmail.com')
            assert in_user == out_user and isinstance(out_user, User)

    def test_add_remove_role(self):
        """
        PROCEDURE:
        - create a test role object
        - retrieve test user from db
        - assign new role object to the user
        - write the user to the db
        - retrieve same user from db
        - assert that the given role name string is in user role list

        UNIQUE COVERAGE:
        - flask-security find_or_create_role()
        - flask-security find_role()
        - flask-security create_role()
        - flask-security add_role_to_user()
        - ORM convert_attr_to_dynamo()
        - ORM convert_attr_from_dynamo()
        - Role class
        """
        with self.app.app_context():
            new_role = self._users.find_or_create_role(
                name='testrole',
                description='testdescript'
            )
            user = self._users.get_user('ian.f.t.wright+1@gmail.com')
            self._users.add_role_to_user(user, new_role)
            modified_user = self._users.get_user('ian.f.t.wright+1@gmail.com')
            assert modified_user.roles[0] == 'testrole'

    """
    UNTESTED:
    - delete_model (dynamo)
    - scan (BaseTable)
    - delete (UserTable)
    - update (UserTable)
    - find (security)
    """


@pytest.mark.usefixtures('gv_conns')
class TestFriendModels:

    def test_get_friendship(self):
        """
        PROCEDURE:
        - create two test users
        - send a friendship request between the two users, (write to db)
        - retrieve that friendship from the db, and confirm it (write to db)
        - retrieve the same friendship from the db again, asert that it is properly confirmed

        UNIQUE COVERAGE:
        - send_friend_request (FriendManager)
        - get_friendship (FriendTable)
        - confirm_friend_request (FriendManager)
        - Friendship class
        """
        with self.app.app_context():
            user1 = self._users.create_user(
                email='ian.f.t.wright+1@gmail.com',
                password='password',
                first_name='ian1',
                last_name='wright'
            )
            user2 = self._users.create_user(
                email='ian.f.t.wright+2@gmail.com',
                password='password',
                first_name='ian2',
                last_name='wright'
            )
            self._friends.send_friend_request(
                sender_user=user1,
                receiver_email=user2.email,
                new_user=False
            )
            confirmed = self._friends.confirm_pending_request(user2.email, user1.email)
            assert confirmed.confirmed_at is not None

    def test_list_friends(self):
        """
        PROCEDURE:
        - create a third and fourth test user
        - send a friendship request from user3 to user2, (write to db)
        - confirm that friendship
        - send a friendship request from user1 to user4 (unconfirmed), (write to db)
        - call list_pending_requests for user4
        - assert that list is length 1, and friend email belongs to user1
        - call list_confirmed_friendships for user2
        - asert that list is length 2, and emails belong to user1 and user3

        UNIQUE COVERAGE:
        - list_pending_requests_payload (FriendManager)
        - list_pending_received_requests (ORM)
        - list_sent_requests_payload (FriendManager)
        - list_sent_received_requests (ORM)
        - get_security_payload()
        """
        with self.app.app_context():
            user1 = self._users.get_user('ian.f.t.wright+1@gmail.com')
            user2 = self._users.get_user('ian.f.t.wright+2@gmail.com')
            user3 = self._users.create_user(
                email='ian.f.t.wright+3@gmail.com',
                password='password',
                first_name='ian3',
                last_name='wright'
            )
            user4 = self._users.create_user(
                email='ian.f.t.wright+3@gmail.com',
                password='password',
                first_name='ian4',
                last_name='wright'
            )
            self._friends.send_friend_request(
                sender_user=user3,
                receiver_email=user2.email,
                new_user=False
            )
            self._friends.confirm_pending_request(user3.email, user2.email)
            self._friends.send_friend_request(
                sender_user=user1,
                receiver_email=user4.email,
                new_user=False
            )

            errors = []
            pending = self._friends.list_pending_receieved_requests_payload(user4.email)
            print(pending)
            if len(pending) != 1:
                errors.append('pending friend list wrong length')
            if len(pending) ==1 and pending[0]['email'] != 'ian.f.t.wright+1@gmail.com':
                errors.append('pending email value wrong')

            confirmed = self._friends.list_confirmed_friends_payload(user2.email)
            if len(confirmed) != 2:
                errors.append('confirmed friend list wrong length')
            if 'ian.f.t.wright+1@gmail.com' not in list(map(lambda payload: payload['email'], confirmed)):
                errors.append('confirmed email value wrong')
            if 'ian.f.t.wright+3@gmail.com' not in list(map(lambda payload: payload['email'], confirmed)):
                errors.append('confirmed email value wrong')

            assert not errors, "friend errors occured:\n{}".format("\n".join(errors))


@pytest.mark.usefixtures('gv_conns')
class TestShareModels:
    def test_create_retrieve_article(self):
        """
        PROCEDURE:
        - create a new article
        - write it to db
        - retrieve it from db
        - assert that retrieved article matches original

        UNIQUE COVERAGE:
        -
        """
        with self.app.app_context():
            in_article = Article(
                url='url1',
                domain='domain1',
                title='title1',
                content='content1',
                date_published=datetime.datetime.utcnow(),
                image_url='img1',
                word_count=10,
                excerpt='excerpt1'
            )
            self._db.put_model(in_article)
            out_article = self._db.article_table.get_article('url1')
            assert in_article == out_article

    def test_create_delete_article(self):
        """
        PROCEDURE:
        - delete the test article from db
        - assert that attempting to retrieve it again yields nothing

        UNIQUE COVERAGE:
        -
        """
        with self.app.app_context():
            self._db.article_table.delete_article('url1')
            out_article = self._db.article_table.get_article('url1')
            assert out_article == None

    def test_create_retrieve_share(self):
        with self.app.app_context():
            self._shares.generate_share(
                sender_email='ian.f.t.wright+1@gmail.com',
                receiver_email='ian.f.t.wright+2@gmail.com',
                url='https://techcrunch.com/2017/10/18/cnn-gets-a-first-of-its-kind-waiver-to-fly-drones-over-crowds/'
            )
            retrieved_share = self._db.share_table.get_share(
                sender_email='ian.f.t.wright+1@gmail.com',
                receiver_email='ian.f.t.wright+2@gmail.com',
                url='https://techcrunch.com/2017/10/18/cnn-gets-a-first-of-its-kind-waiver-to-fly-drones-over-crowds/'
            )
            retrieved_article=self._db.article_table.get_article(
                'https://techcrunch.com/2017/10/18/cnn-gets-a-first-of-its-kind-waiver-to-fly-drones-over-crowds/'
            )
            assert retrieved_share.url == retrieved_article.url