import pytest
import backend.posts as posts

TEST_POSTS_WITH_ID = [
    {"id": 1, "title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "author": "Someone", "date": "2020-04-20", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "author": "Someone", "date": "2022-04-11", "content": "This is the third post."},
    {"id": 4, "title": "012345", "author": "Someone", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"id": 5, "title": "WWWWWWWW", "author": "Someone", "date": "2024-10-12", "content": "1"},
    {"id": 6, "title": "🤯🤷‍♂️😘👍😴", "author": "Someone", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"},
]

TEST_POSTS_WITHOUT_ID = [
    {"title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"title": "Second post", "author": "Someone", "date": "2020-04-20", "content": "This is the second post."},
    {"title": "Third post", "author": "Someone", "date": "2022-04-11", "content": "This is the third post."},
    {"title": "012345", "author": "Someone", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"title": "WWWWWWWW", "author": "Someone", "date": "2024-10-12", "content": "1"},
    {"title": "🤯🤷‍♂️😘👍😴", "author": "Someone", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"},
]


@pytest.mark.parametrize("post", TEST_POSTS_WITHOUT_ID)
def test_validate_post_all_valid(post):
    assert posts.validate_post(post) is True

@pytest.mark.parametrize("post", TEST_POSTS_WITH_ID)
def test_validate_post_all_invalid(post):
    assert posts.validate_post(post) is False

@pytest.mark.parametrize("post", TEST_POSTS_WITH_ID)
def test_validate_post_with_id_all_valid(post):
    assert posts.validate_post_with_id(post) is True

@pytest.mark.parametrize("post", TEST_POSTS_WITHOUT_ID)
def test_validate_post_with_id_all_invalid(post):
    assert posts.validate_post_with_id(post) is False