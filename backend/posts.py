"""
A module to handle the blog posts.
"""
import logging

logging.basicConfig(
    filename='blog_backend.log',  # Specify the log file name
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'  # Specify
)
logger = logging.getLogger(__name__)


POSTS = [
    {"id": 1, "title": "First post", "author": "Someone", "date": "2020-03-25", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "author": "Someone", "date": "2020-04-20", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "author": "Someone", "date": "2022-04-11", "content": "This is the third post."},
    {"id": 4, "title": "012345", "author": "Someone", "date": "2023-09-11", "content": "Ridiculous \\"},
    {"id": 5, "title": "WWWWWWWW", "author": "Someone", "date": "2024-10-12", "content": "1"},
    {"id": 6, "title": "🤯🤷‍♂️😘👍😴", "author": "Someone", "date": "2024-01-11", "content": "🤯🤷‍♂️😘👍😴"},
]


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
    if len(post.keys()) != 4:
        return False
    logger.info('INFO post validated: %s', post)
    return True


def validate_post_with_id(post):
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
    if not is_valid:
        return None
    if len(POSTS) == 0:
        new_id = 1
    else:
        new_id = max(int(post.get('id')) + 1 for post in POSTS)
    new_post['id'] = new_id
    POSTS.append(new_post)
    logger.info('INFO new post added: %s', new_post)
    return new_post


def get_all(sort_by = None, sort_direction = None):
    """
    Return all blog posts.
    :param sort_by: (str) the blog post sort key
    :param sort_direction: (str) the blog post sort direction asc/desc
    """
    if sort_by is None and sort_direction is None:
        return POSTS
    if  sort_by is not None and sort_by not in ['title', 'content']:
        return None
    if sort_direction is not None and (sort_direction not in ['asc', 'desc'] or sort_by is None):
        return None
    sorted_posts = sorted(POSTS, key = lambda post: post['title'] if sort_by == 'title' else post['content'])
    if sort_direction == 'desc':
        sorted_posts.reverse()
    return sorted_posts


def delete_post(post_id):
    """ Delete a post """
    for post in list(POSTS):
        if int(post.get('id')) == int(post_id):
            POSTS.remove(post)
            return post
    return None


def update_post(post_id, new_post):
    """ Update blog post """
    if not isinstance(new_post, dict):
        return None
    for key in new_post.keys():
        if key not in ('title', 'content'):
            return None
    for value in new_post.values():
        if not isinstance(value, str):
            return None
        if len(value) == 0:
            return None
    post_to_update = get_post(post_id)
    if post_to_update is None:
        return None
    post_to_update.update(new_post)
    return post_to_update


def get_post(post_id):
    """ Find the blog post """
    for post in POSTS:
        if int(post.get('id')) == int(post_id):
            return post
    return None


def search_posts(title, content):
    """ Find the blog posts that match the search criteria """
    found_posts = []
    for post in POSTS:
        if title is not None and title.lower() in post.get('title', "").lower():
            found_posts.append(post)
        if content is not None and content.lower() in post.get('content', "").lower():
            found_posts.append(post)
    return found_posts