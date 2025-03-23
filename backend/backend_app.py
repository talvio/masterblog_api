""" Simple blog post API """

import logging
from pathlib import Path
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
try:
    import backend.posts as posts
except ModuleNotFoundError:
    import posts

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file


API_INSTRUCTIONS = API_INSTRUCTIONS = {
    "endpoints": [
        {
            "description": "List all posts. Output is paginated.",
            "method": "GET",
            "url": "/api/posts",
            "query_params": {
                "sort": "Field to sort by (optional)",
                "direction": "Sorting direction (asc or desc, optional)",
                "page": "Page number for pagination (optional, default=1)",
                "limit": "Number of items per page (optional, default=10)"
            }
        },
        {
            "description": "Search for posts based on criteria.",
            "method": "GET",
            "url": "/api/posts/search",
            "query_params": {
                "title": "Search by title (optional)",
                "content": "Search by content (optional)",
                "author": "Search by author (optional)",
                "date": "Search by date (optional)",
                "page": "Page number for pagination (optional, default=1)",
                "limit": "Number of items per page (optional, default=10)"
            }
        },
        {
            "description": "Add a new blog post.",
            "method": "POST",
            "url": "/api/posts",
            "body": {
                "title": "Title for the post (mandatory)",
                "author": "Author for the post (mandatory)",
                "date": "Date for the post in the format yyyy-mm-dd (mandatory)",
                "content": "Content for the post (mandatory)"
            }
        },
        {
            "description": "Delete a blog post.",
            "method": "DELETE",
            "url": "/api/posts/<id>",
            "note": "<id> should be the blog post ID."
        },
        {
            "description": "Update a blog post.",
            "method": "PUT",
            "url": "/api/posts/<id>",
            "note": "<id> should be the blog post ID.",
            "body": {
                "title": "Updated title for the post (optional)",
                "author": "Updated author for the post (optional)",
                "date": "Updated date for the post in the format yyyy-mm-dd (optional)",
                "content": "Updated content for the post (optional)"
            }
        }
    ],
    "error_responses": {
        "400": {
            "error": "Bad Request",
            "message": "Invalid input or request format."
        },
        "404": {
            "error": "Not Found",
            "message": "Requested resource does not exist."
        },
        "405": {
            "error": "Method Not Allowed",
            "message": "Wrong HTTP method used for this endpoint."
        },
        "500": {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }
    }
}


DELETED_POST_MESSAGE = "Post with id {id} has been deleted successfully."

logging.basicConfig(
    filename= Path(__file__).parent  / 'log/blog_backend.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """ Get all posts and send them through the API """
    sort_by = request.args.get('sort', None)
    sort_direction = request.args.get('direction', None)
    app.logger.info('Request to get posts sorted by %s %s.',
                    sort_by, sort_direction

    )
    all_posts = posts.get_all(sort_by, sort_direction)
    if all_posts is None and sort_by is None and sort_direction is None:
        app.logger.debug('DEBUG getting posts failed.')
        return internal_server_error("Getting posts failed.")
    if all_posts is None and (sort_by is not None or sort_direction is not None):
        app.logger.debug('DEBUG getting sorted posts failed.')
        return bad_request("Wrong format for sorting posts.")
    return paginated_posts(all_posts)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """ Get all posts that match the search criteria and send them through the API """
    # Handle the GET request
    title = request.args.get('title', None)
    content = request.args.get('content', None)
    author = request.args.get('author', None)
    date = request.args.get('date', None)
    app.logger.info('Searching for title:%s author:%s date:%s content:%s.',
        title, author, date, content
    )
    return paginated_posts(posts.search_posts(title, content, author, date))


@app.route('/api/posts', methods=['POST'])
def add_post():
    """ Add a new blog post """
    app.logger.info('POST request received for /api/posts')
    new_post = request.get_json()
    app.logger.info('Add post request: %s', new_post)
    added_post = posts.add_post(new_post)
    if added_post is None:
        app.logger.debug('New post not accepted: %s.', new_post)  # Log a message
        return bad_request("Wrong post format.")

    return jsonify(added_post)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """ Delete a blog post """
    app.logger.info('DELETE request received for /api/posts/%s', post_id)
    deleted_post = posts.delete_post(post_id)
    if deleted_post is None:
        app.logger.debug('%s was not deleted.', post_id)  # Log a message
        return not_found_error("No such post was found.")
    app.logger.debug('Post %s was deleted.', post_id)
    return jsonify({
        'message': DELETED_POST_MESSAGE.format(id=post_id)
    })


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update(post_id):
    """ Update a blog post """
    app.logger.info('PUT request received for /api/posts/%s', post_id)
    post_to_update = request.get_json()
    app.logger.debug('Update post: %s %s', post_id, post_to_update)
    updated_post = posts.update_post(post_id, post_to_update)
    if updated_post is None:
        app.logger.debug('Post update not accepted id:%s update:%s.',
            post_id, post_to_update
        )
        return not_found_error("Wrong post format or post not found.")
    app.logger.debug('Post update successful: id:%s update:%s.',
        post_id, post_to_update
    )
    return jsonify(updated_post)


@app.errorhandler(400)
def bad_request(error):
    """ What to return when someone is accessing the API in a wrong way. """
    response = {
        "error": "Bad Request",
        "message": str(error),
        "instructions": API_INSTRUCTIONS
    }
    return jsonify(response), 400


@app.errorhandler(404)
def not_found_error(error):
    """
    What to return when someone is accessing the API with the wrong post Id or
    asking for some other resource which does not exist.
    """
    return jsonify({
        "error": "Bad Request",
        "message": str(error),
        "instructions": API_INSTRUCTIONS
    }), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    """ What to return when someone is accessing the right API with the wrong method. """
    return jsonify({
        "error": "Bad Request",
        "message": str(error),
        "instructions": API_INSTRUCTIONS
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    """ Show this when we find something has really gone wrong. """
    return jsonify({
        "error": "Internal Server Error",
        "message": str(error)
    }), 500


def paginated_posts(posts_to_paginate):
    """
    Paginates the posts returned by the API.
    :param posts_to_paginate: posts to paginate
    :return: paginated posts in json format
    """
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_posts_list = posts_to_paginate[start_index:end_index]
    return jsonify(paginated_posts_list)


if __name__ == '__main__' and "pytest" not in sys.modules:
    """ Starts the Flask app if this is the main python file and not run by unit tests."""
    app.run(host="0.0.0.0", port=5002, debug=True)
