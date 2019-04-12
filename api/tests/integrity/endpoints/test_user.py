import pytest

from default_users import default_users
from models import User
from redis_store import store


@pytest.mark.parametrize("username,password,http_code,json", (
        ('user1', 'short', 400, {
            'password': ['Shorter than minimum length 6.'],
            'username': ['Shorter than minimum length 6.']
        }),
        ('username1', 'short', 400, {
            'password': ['Shorter than minimum length 6.'],
        }),
        ('short', 'passsword', 400, {
            'username': ['Shorter than minimum length 6.'],
        }),
        ('username_wrong', 'correctpwd1', 404, {
        }),
        ('username1', 'wrong_password', 422, {
        }),
))
def test_auth_login_input_data_validation(
        client, username, password, http_code, json):

    rsp = client.post('/users/login', json={
        'username': username,
        'password': password
    })
    assert rsp.status_code == http_code
    assert rsp.json == json


@pytest.mark.parametrize("username,password", [
    (item['username'], item['password']) for item in default_users
])
def test_auth_login_success(client, username, password):
    data = {
        'username': username,
        'password': password
    }

    response = client.post('/users/login', json=data)
    assert response.status_code == 200
    assert 'token' in response.json
    user_id = store.get_token_data(response.json['token'])
    assert user_id is not None
    local_user = User.get_by_username(username)
    token_user = User.query.get(user_id)
    assert local_user == token_user


@pytest.mark.parametrize("username,password", [
    (item['username'], item['password']) for item in default_users
])
def test_user_auth_logs(client, username, password):
    data =dict(username=username, password=password)
    response = client.post('/users/login', json=data)
    headers = {'X-API-TOKEN': response.json['token']}

    # test empty params
    data = dict()
    response = client.get('/users/auth/logs', headers=headers, data=data)
    assert response.status_code == 200
    assert len(response.json) > 0

    # test empty params
    response = client.get('/users/auth/logs', headers=headers)
    assert response.status_code == 200
    assert len(response.json) > 0

    # test get auth logs with `username`
    response = client.get('/users/auth/logs?users=username1&per_page=5', headers=headers)
    assert response.status_code == 200
    assert len(response.json) > 0

    assert (
            len(response.json) ==
            len([row for row in response.json if row['username'] == 'username1'])
    )

    # test get auth logs with `page`
    response = client.get('/users/auth/logs?page=1&users=username1&per_page=5', headers=headers)
    assert response.status_code == 200

    # test get auth logs with not existed `page` num
    response = client.get('/users/auth/logs?page=100000&users=username1&per_page=5', headers=headers)
    assert response.status_code == 404
