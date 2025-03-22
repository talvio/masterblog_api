import pytest
import json
import os.path
import backend.posts as posts

TEST_POSTS_WITH_ID = [
    {"id": 1, "title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "author": "Someone", "date": "2020-04-20", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "author": "Someone", "date": "2022-04-11", "content": "This is the third post."},
    {"id": 4, "title": "012345", "author": "Someone", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"id": 5, "title": "WWWWWWWW", "author": "Someone", "date": "2024-10-12", "content": "1"},
    {"id": 6, "title": "🤯🤷‍♂️😘👍😴", "author": "Someone", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"}
]

TEST_POSTS_WITHOUT_ID = [
    {"title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"title": "Second post", "author": "Someone", "date": "2020-04-20", "content": "This is the second post."},
    {"title": "Third post", "author": "Someone", "date": "2022-04-11", "content": "This is the third post."},
    {"title": "012345", "author": "Someone", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"title": "WWWWWWWW", "author": "Someone", "date": "2024-10-12", "content": "1"},
    {"title": "🤯🤷‍♂️😘👍😴", "author": "Someone", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"},
]

TEST_POSTS_FILE_1 = os.path.join("tests", "data", "posts.json")
TEST_POSTS_FILE_2 = os.path.join("tests", "data", "posts_no_file.json")
TEST_POSTS_FILE_3 = os.path.join("tests", "data", "posts_empty_file.json")
TEST_POSTS_FILE_4 = os.path.join("tests", "data", "posts_wrong_file.json")
PATH_DOES_NOT_EXIST = os.path.join("tests", "data", "no_dir", "no_dir", "posts_wrong_file.json")


@pytest.fixture(scope='session')
def test_files():
    with open(TEST_POSTS_FILE_1, 'w', encoding='utf-8') as json_file:
        json.dump(TEST_POSTS_WITH_ID, json_file)

    if os.path.exists(TEST_POSTS_FILE_2): os.remove(TEST_POSTS_FILE_2)

    with open(TEST_POSTS_FILE_3, 'w', encoding='utf-8') as json_file:
        pass

    with open(TEST_POSTS_FILE_4, 'w', encoding='utf-8') as file:
        file.writelines("This is not json file.")


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


def test_read_posts_nominal(test_files):
    posts_all = posts.read_posts(TEST_POSTS_FILE_1)
    assert posts_all == TEST_POSTS_WITH_ID


def test_read_posts_no_file(test_files):
    posts_all = posts.read_posts(TEST_POSTS_FILE_2)
    assert posts_all == []


def test_read_posts_empty_file(test_files):
    posts_all = posts.read_posts(TEST_POSTS_FILE_3)
    assert posts_all == []


def test_read_posts_non_json_file(test_files):
    posts_all = posts.read_posts(TEST_POSTS_FILE_4)
    assert posts_all == []


def test_save_post_no_path(test_files):
    with pytest.raises(FileNotFoundError, match="No such file or directory"):
        posts.save_posts(TEST_POSTS_WITH_ID, PATH_DOES_NOT_EXIST)
