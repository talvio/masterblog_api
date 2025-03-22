import pytest
import json
import backend.backend_app

TEST_POSTS = [
    {"title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"title": "Second post", "author": "Someone", "date": "2020-04-20", "content": "This is the second post."},
    {"title": "Third post", "author": "Someone", "date": "2022-04-11", "content": "This is the third post."},
    {"title": "012345", "author": "Someone", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"title": "WWWWWWWW", "author": "Someone", "date": "2024-10-12", "content": "1"},
    {"title": "🤯🤷‍♂️😘👍😴", "author": "Someone", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"},
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
    for post_num in range(len(TEST_POSTS) + 20):
        client.delete(f'/api/posts/{post_num}')
    for post_num, post in enumerate(TEST_POSTS):
        response = client.post('/api/posts',
                                data=json.dumps(post),
                                content_type='application/json'
        )
        assert response.status_code == 200



def test_get_posts(client, set_posts):
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
    response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == [{'content': 'This is the second post.', 'id': 2, 'title': 'Second post'}]
    search_criteria = {'content': 'SeCOnd'}
    response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == [{'content': 'This is the second post.', 'id': 2, 'title': 'Second post'}]
    search_criteria = {'title': '🤷'}
    response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == [{"title": "🤯🤷‍♂️😘👍😴", 'id': 6, "content": "🤯🤷‍♂️😘👍😴"}]
    search_criteria = {'content': 'not in the list'}
    response = client.get('/api/posts/search', query_string=search_criteria)
    assert response.status_code == 200
    assert response.json == []


def test_add_post(client, set_posts):
    post = {
        'content': 'Content contentContent contentContent contentContent contentContent content.',
        'title': 'Title title',
        'date': '2020-03-25',
        'author': 'Someone',
    }
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
        'id': 3,
        'date': '2020-03-25',
        'author': 'Someone',
    }
    response = client.post('/api/posts',
                            data=json.dumps(post),
                            content_type='application/json'
                           )
    assert response.status_code == 400
    assert '{"error":"Bad Request",' in response.get_data(as_text=True)


def test_delete_post(client, set_posts):
    response = client.delete('/api/posts/1')
    assert response.status_code == 200
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    assert response.json == {'message': 'Post with id 1 has been deleted successfully.'}


def test_delete_wrong_post(client, set_posts):
    wrong_id = len(TEST_POSTS) + 1
    response = client.delete(f'/api/posts/{wrong_id}')
    assert response.status_code == 404
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    assert '{"error":"Bad Request","instructions"' in response.get_data(as_text=True)


def test_put_empty_post(client, set_posts):
    post_update = {
    }
    response = client.put('/api/posts/2',
                          data=json.dumps(post_update),
                          content_type='application/json'
                          )
    assert response.status_code == 200
    assert response.json == {
        "content": "This is the second post.",
        "id": 2,
        "title": "Second post",
        "author": "Someone",
        "date": "2020-04-20"}


def test_put_post(client, set_posts):
    post_update = {
        'content': 'Content content Content.',
        'title': 'Title title',
        "author": "Somebody",
    }
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
    response = client.put('/api/posts/42',
                            data=json.dumps(post_update),
                            content_type='application/json'
                           )
    assert response.status_code == 404


def test_get_sorted_posts_title(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'title'}
    response = client.get('/api/posts', query_string=parameters)
    #response = client.get('/api/posts')
    assert response.status_code == 200
    #print(response.get_data(as_text=True))  # e.g., '{"posts": [...]}'
    print(TEST_POSTS)
    posts = sorted(posts, key=lambda post: post['title'])
    returned_posts = json.loads(response.data)
    print(posts)
    print(returned_posts)
    #exit()
    for post_num in range(len(posts)):
        assert posts[post_num].get('title') == returned_posts[post_num].get('title')
        assert posts[post_num].get('content') == returned_posts[post_num].get('content')

def test_get_sorted_posts_content(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'content'}
    response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 200
    posts = sorted(posts, key=lambda post: post['content'])
    returned_posts = json.loads(response.data)
    for post_num in range(len(posts)):
        assert posts[post_num].get('title') == returned_posts[post_num].get('title')
        assert posts[post_num].get('content') == returned_posts[post_num].get('content')

def test_get_sorted_posts_content_desc(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'content', 'direction': 'desc'}
    response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 200
    returned_posts = json.loads(response.data)
    posts = sorted(posts, key=lambda post: post['content'])
    posts.reverse()
    for post_num in range(len(posts)):
        assert posts[post_num].get('title') == returned_posts[post_num].get('title')
        assert posts[post_num].get('content') == returned_posts[post_num].get('content')


def test_wrong_sort_fields_get_sorted_posts(client, set_posts, posts=TEST_POSTS):
    parameters = {'sort': 'cont', 'direction': 'desc'}
    response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)

    parameters = {'direction': 'asc'}
    response = client.get('/api/posts', query_string=parameters)
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)