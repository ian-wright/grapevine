from grapevine import create_app
import pytest


@pytest.fixture
def app(request):
    return create_app('loctest')


@pytest.fixture
def client(request, app):
    return app.test_client()


def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login(client, app):
    """Make sure login and logout works"""
    rv = login(client, 'ian.f.t.wright@gmail.com', 'password')
    assert b'You were logged in' in rv.data

    rv = login(client, app.config['USERNAME'],
               app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in rv.data
