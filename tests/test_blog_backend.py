import pytest
from unittest import mock
import json
from pathlib import Path
import backend.backend_app


TEST_POSTS_FILE = Path(__file__).parent / "data/posts.json"

TEST_POSTS = [
    {"title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"title": "Second post", "author": "Somebody", "date": "2020-04-20", "content": "This is the second post."},
    {"title": "Third post", "author": "Someone", "date": "2022-04-11", "content": "This is the third post."},
    {"title": "012345", "author": "Somebody", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"title": "WWWWWWWW", "author": "Jack", "date": "2024-10-12", "content": "1"},
    {"title": "🤯🤷‍♂️😘👍😴", "author": "Somebody", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"},
]

@pytest.fixture(scope='session')
def client():
    app = backend.backend_app.app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def set_posts(client):
    """
    Start each test with the same post content
    :param client: test client
    :return: None
    """
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        for post_num in range(len(TEST_POSTS) + 20):
            client.delete(f'/api/posts/{post_num}')
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        for post_num, post in enumerate(TEST_POSTS):
            response = client.post('/api/posts',
                                    data=json.dumps(post),
                                    content_type='application/json'
            )
            assert response.status_code == 200


def test_get_posts(client, set_posts):
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts')
    assert response.status_code == 200
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    returned_posts = json.loads(response.data)
    for post_num in range(len(TEST_POSTS)):
        assert TEST_POSTS[post_num].get('title') == returned_posts[post_num].get('title')
        assert TEST_POSTS[post_num].get('content') == returned_posts[post_num].get('content')
        assert post_num + 1 == int(returned_posts[post_num].get('id'))


def test_search_posts(client, set_posts):
    search_criteria = {'title': 'second',}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    expected_result = TEST_POSTS[1].copy()
    expected_result['id'] = 2
    assert response.json == [expected_result,]
    search_criteria = {'content': 'SeCOnd'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == [expected_result,]
    search_criteria = {'title': '🤷'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    expected_result = TEST_POSTS[5].copy()
    expected_result['id'] = 6
    assert response.json == [expected_result,]
    search_criteria = {'content': 'not in the list'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == []

def test_search_posts_author(client, set_posts):
    search_criteria = {'author': 'Jack'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == [{'author': 'Jack', 'content': '1', 'date': '2024-10-12', 'id': 5, 'title': 'WWWWWWWW'}]


def test_search_posts_date(client, set_posts):
    search_criteria = {'date': '2024'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == [
        {'author': 'Jack', 'content': '1', 'date': '2024-10-12', 'id': 5, 'title': 'WWWWWWWW'},
        {"title": "🤯🤷‍♂️😘👍😴", "author": "Somebody", "date": "2024-01-11", 'id': 6, "content": "🤯🤷‍♂️😘👍😴"}
    ]


def test_add_post(client, set_posts):
    post = {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'title': 'Title title',
        'date': '2020-03-25',
        'author': 'Someone',
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.post('/api/posts',
                                data=json.dumps(post),
                                content_type='application/json'
                               )
    assert response.status_code == 200
    assert response.json == {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'id': 7,
        'title': 'Title title',
        'date': '2020-03-25',
        'author': 'Someone',
    }


def test_add_post_wrong_format(client, set_posts):
    post = {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'title': 'Title title',
        'title2': 'Title title',
        'date': '2020-03-25',
        'author': 'Someone',
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.post('/api/posts',
                                data=json.dumps(post),
                                content_type='application/json'
                               )
    assert response.status_code == 400
    assert '{"error":"Bad Request",' in response.get_data(as_text=True)
    post = {
        'title': 'Title title',
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.post('/api/posts',
                               data=json.dumps(post),
                               content_type='application/json'
                               )
    assert response.status_code == 400
    assert '{"error":"Bad Request",' in response.get_data(as_text=True)
    post = {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'title': 'Title title',
        'id': 3,
        'date': '2020-03-25',
        'author': 'Someone',
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.post('/api/posts',
                                data=json.dumps(post),
                                content_type='application/json'
                               )
    assert response.status_code == 400
    assert '{"error":"Bad Request",' in response.get_data(as_text=True)


def test_delete_post(client, set_posts):
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.delete('/api/posts/1')
    assert response.status_code == 200
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    assert response.json == {'message': 'Post with id 1 has been deleted successfully.'}


def test_delete_wrong_post(client, set_posts):
    wrong_id = len(TEST_POSTS) + 1
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.delete(f'/api/posts/{wrong_id}')
    assert response.status_code == 404
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    assert '{"error":"Bad Request","instructions"' in response.get_data(as_text=True)


def test_put_empty_post(client, set_posts):
    post_update = {
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.put('/api/posts/2',
                              data=json.dumps(post_update),
                              content_type='application/json'
                              )
    assert response.status_code == 200
    assert response.json == {
        "content": "This is the second post.",
        "id": 2,
        "title": "Second post",
        "author": "Somebody",
        "date": "2020-04-20"}


def test_put_post(client, set_posts):
    post_update = {
        'content': 'Content content Content.',
        'title': 'Title title',
        "author": "Somebody",
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.put('/api/posts/2',
                                data=json.dumps(post_update),
                                content_type='application/json'
                               )
    assert response.status_code == 200
    assert response.json == {
        "content": "Content content Content.",
        "id": 2,
        "title": "Title title",
        "author": "Somebody",
        "date": "2020-04-20"
    }


def test_put_wrong_post(client, set_posts):
    post_update = {
        "content": "This is the second post.",
        "title": "Second post",
        "author": "Someone",
        "date": "2020-04-20"
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.put('/api/posts/42',
                                data=json.dumps(post_update),
                                content_type='application/json'
                               )
    assert response.status_code == 404

def test_put_wrong_post_wrong_date(client, set_posts):
    post_update = {
        "content": "This is the second post.",
        "title": "Second post",
        "author": "Someone",
        "date": "2020-04-32"
    }
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.put('/api/posts/2',
                                data=json.dumps(post_update),
                                content_type='application/json'
                               )
    assert response.status_code == 404


def test_get_sorted_posts_title(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'title'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 200
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    posts = sorted(posts, key=lambda post: post['title'])
    returned_posts = json.loads(response.data)
    for post_num in range(len(posts)):
        assert posts[post_num].get('title') == returned_posts[post_num].get('title')
        assert posts[post_num].get('content') == returned_posts[post_num].get('content')


def test_get_sorted_posts_content(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'content'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 200
    posts = sorted(posts, key=lambda post: post['content'])
    returned_posts = json.loads(response.data)
    for post_num in range(len(posts)):
        assert posts[post_num].get('title') == returned_posts[post_num].get('title')
        assert posts[post_num].get('content') == returned_posts[post_num].get('content')


def test_get_sorted_posts_content_desc(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'content', 'direction': 'desc'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 200
    returned_posts = json.loads(response.data)
    print(returned_posts)
    posts = sorted(posts, key=lambda post: post['content'])
    posts.reverse()
    print(posts)
    for post_num in range(len(posts)):
        assert posts[post_num].get('title') == returned_posts[post_num].get('title')
        assert posts[post_num].get('content') == returned_posts[post_num].get('content')


def test_wrong_sort_fields_get_sorted_posts(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'cont', 'direction': 'desc'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)

    parameters = {'direction': 'asc'}
    with mock.patch("backend.backend_app.posts.POSTS_FILE", TEST_POSTS_FILE):
        response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)