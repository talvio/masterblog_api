import pytest
import json
import backend.backend_app


@pytest.fixture(scope='session')
def client():
    app = backend.backend_app.app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_posts(client):
    response = client.get('/api/posts')
    assert response.status_code == 200
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    assert response.json == [
            {
                'content': 'This is the first post.',
                'id': 1,
                'title': 'First post'
            },
            {   'content': 'This is the second post.',
                'id': 2,
                'title': 'Second post'
            }
        ]

def test_add_post(client):
    post = {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'title': 'Title title'
    }
    response = client.post('/api/posts',
                            data=json.dumps(post),
                            content_type='application/json'
                           )
    assert response.status_code == 200
    assert response.json == {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'id': 3,
        'title': 'Title title'
    }


def test_add_post_wrong_format(client):
    post = {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'title': 'Title title',
        'title2': 'Title title'
    }
    response = client.post('/api/posts',
                            data=json.dumps(post),
                            content_type='application/json'
                           )
    assert response.status_code == 400
    assert '{"error":"Bad Request",' in response.get_data(as_text=True)
    post = {
        'title': 'Title title',
    }
    response = client.post('/api/posts',
                           data=json.dumps(post),
                           content_type='application/json'
                           )
    assert response.status_code == 400
    assert '{"error":"Bad Request",' in response.get_data(as_text=True)
    post = {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'title': 'Title title',
        'id': 3
    }
    response = client.post('/api/posts',
                            data=json.dumps(post),
                            content_type='application/json'
                           )
    assert response.status_code == 400
    assert '{"error":"Bad Request",' in response.get_data(as_text=True)


def test_delete_post(client):
    response = client.delete('/api/posts/1')
    assert response.status_code == 200
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    assert response.json == {'message': 'Post with id 1 has been deleted successfully.'}


def test_delete_wrong_post(client):
    response = client.delete('/api/posts/4')
    assert response.status_code == 404
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    assert '{"error":"Bad Request","instructions"' in response.get_data(as_text=True)


def test_put_empty_post(client):
    post_update = {
    }
    response = client.put('/api/posts/2',
                          data=json.dumps(post_update),
                          content_type='application/json'
                          )
    assert response.status_code == 200
    assert response.json == {'content': 'This is the second post.', 'id': 2, 'title': 'Second post'}


def test_put_post(client):
    post_update = {
        'content': 'Content content Content.',
        'title': 'Title title'
    }
    response = client.put('/api/posts/2',
                            data=json.dumps(post_update),
                            content_type='application/json'
                           )
    assert response.status_code == 200
    assert response.json == {'content': 'Content content Content.', 'id': 2, 'title': 'Title title'}


def test_put_wrong_post(client):
    post_update = {
        'content': 'Content content Content.',
        'title': 'Title title'
    }
    response = client.put('/api/posts/42',
                            data=json.dumps(post_update),
                            content_type='application/json'
                           )
    assert response.status_code == 404
