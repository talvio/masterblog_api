"""
A module to handle the blog posts.
"""
import logging
from datetime import datetime
import json
import os.path

logging.basicConfig(
    filename='blog_backend.log',  # Specify the log file name
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'  # Specify
)
logger = logging.getLogger(__name__)

POSTS_FILE = os.path.join("data", "posts.json")

POSTS = [
    {"id": 1, "title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "author": "Somebody", "date": "2020-04-20", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "author": "Jack", "date": "2022-04-11", "content": "This is the third post."},
    {"id": 4, "title": "012345", "author": "Hugh", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"id": 5, "title": "WWWWWWWW", "author": "Kurt", "date": "2024-10-12", "content": "1"},
    {"id": 6, "title": "🤯🤷‍♂️😘👍😴", "author": "Duck", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"},
]

def read_posts(post_file=None):
    """ Read posts from a json file """
    if post_file is None:
        post_file = POSTS_FILE
    try:
        with open(post_file, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        save_posts([], post_file)
        return []
    except Exception as e:
        logger.error(f"Error: {e}. Unable to read posts from {post_file}. It is not a json file.")
        return []


def save_posts(posts, post_file=None):
    """ Saves blog posts to a file """
    if post_file is None:
        post_file = POSTS_FILE
    with open(post_file, 'w', encoding='utf-8') as json_file:
        json.dump(posts, json_file)


def validate_date(date_string):
    """ Validate that a date in a string format is a valid date in the format yyyy-mm-dd """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_post(post):
    """ Validate the blog post format """
    logger.debug('DEBUG validating post: %s', post)  # Log a message
    if not isinstance(post, dict):
        return False
    for field in ['title', 'author', 'date', 'content']:
        if not isinstance(post.get(field,""), str):
            return False
        if len(post.get(field, "")) == 0:
            return False
    if not validate_date(post.get('date', "")):
        return False
    if len(post.keys()) != 4:
        return False
    logger.info('INFO post validated: %s', post)
    return True


def validate_post_with_id(post):
    """ Validate the blog post format when the post has an ID"""
    if post.get('id', None) is None:
        return False
    if not str(post.get('id', 0)).isdigit():
        return False
    post_copy = post.copy()
    post_copy.pop('id')
    return validate_post(post_copy)


def add_post(new_post):
    """
    Add new blog post
    :param new_post: (dict) the new blog post
    :return: (dict) the new blog post with the unique id added to it
    """
    is_valid =  validate_post(new_post)
    #print(f"post: {new_post} validated as {is_valid}")
    if not is_valid:
        return None
    all_posts = read_posts()
    if len(all_posts) == 0:
        new_id = 1
    else:
        new_id = max(int(post.get('id')) + 1 for post in all_posts)
    new_post['id'] = new_id
    all_posts.append(new_post)
    save_posts(all_posts)
    logger.info('INFO new post added: %s', new_post)
    return new_post


def get_all(sort_by = None, sort_direction = None):
    """
    Return all blog posts.
    :param sort_by: (str) the blog post sort key
    :param sort_direction: (str) the blog post sort direction asc/desc
    """
    all_posts = read_posts()
    if sort_by is None and sort_direction is None:
        return all_posts
    if  sort_by is not None and sort_by not in ['title', 'content', 'author', 'date']:
        return None
    if sort_direction is not None and (sort_direction not in ['asc', 'desc'] or sort_by is None):
        return None
    match sort_by:
        case 'content':
            sorted_posts = sorted(all_posts, key=lambda post: post['content'])
        case 'author':
            sorted_posts = sorted(all_posts, key=lambda post: post['author'])
        case 'date':
            sorted_posts = sorted(all_posts, key=lambda post: post['date'])
        case _:
            sorted_posts = sorted(all_posts, key = lambda post: post['title'])
    if sort_direction == 'desc':
        sorted_posts.reverse()
    return sorted_posts


def delete_post(post_id):
    """ Delete a post """
    all_posts = read_posts()
    for post in list(all_posts):
        if int(post.get('id')) == int(post_id):
            all_posts.remove(post)
            save_posts(all_posts)
            return post
    return None


def update_post(post_id, new_post):
    """ Update blog post """
    if not isinstance(new_post, dict):
        return None
    for key, value in new_post.items():
        if (key not in ('title', 'content', 'author', 'date')
            or not isinstance(value, str)
            or len(value) == 0):
            return None
    if not validate_date(new_post.get('date', "2025-03-22")):
        return None
    all_posts = read_posts()
    for post in all_posts:
        if int(post.get('id')) == int(post_id):
            post.update(new_post)
            save_posts(all_posts)
            return post
    return None


def get_post(post_id):
    """ Find the blog post """
    all_posts = read_posts()
    for post in all_posts:
        if int(post.get('id')) == int(post_id):
            return post
    return None


def search_posts(title, content, author, date):
    """ Find the blog posts that match the search criteria """
    found_posts = []
    all_posts = read_posts()
    for post in all_posts:
        if title is not None and title.lower() in post.get('title', "").lower():
            found_posts.append(post)
        if content is not None and content.lower() in post.get('content', "").lower():
            found_posts.append(post)
        if author is not None and author.lower() in post.get('author', "").lower():
            found_posts.append(post)
        if date is not None and date.lower() in post.get('date', "").lower():
            found_posts.append(post)
    return found_posts
