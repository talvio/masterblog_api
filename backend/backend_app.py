import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import backend.posts as posts

API_INSTRUCTIONS = {
    "endpoints": [
        {
            "description": "Add a new blog post",
            "method": "POST",
            "url": "/api/posts",
            "body": {
                "title": "Your title for the post",
                "content": "Your content for the post"
            }
        },
        {
            "description": "Delete a blog post",
            "method": "DELETE",
            "url": "/api/posts/<id>",
            "note": "<id> should be the blog post ID"
        }
    ]
}

DELETED_POST_MESSAGE = "Post with id {id} has been deleted successfully."

logging.basicConfig(
    filename='blog_backend.log',  # Specify the log file name
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'  # Specify
)


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(posts.get_all())

@app.route('/api/posts', methods=['POST'])
def add_post():
    app.logger.info('POST request received for /api/posts')
    new_post = request.get_json()
    app.logger.debug(f'DEBUG new post: {new_post}')  # Log a message
    added_post = posts.add_post(new_post)
    if added_post is None:
        app.logger.debug(f'DEBUG new post not accepted.')  # Log a message
        return bad_request("Wrong post format.")
    else:
        return jsonify(added_post)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    app.logger.info(f'DELETE request received for /api/posts/{post_id}')
    deleted_post = posts.delete_post(post_id)
    if deleted_post is None:
        app.logger.debug(f'DEBUG {post_id} was not deleted.')  # Log a message
        return not_found_error("No such post was found.")
    else:
        return jsonify({
            'message': DELETED_POST_MESSAGE.format(id=post_id)
        })


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update(post_id):
    app.logger.info(f'PUT request received for /api/posts/{post_id}')
    post_to_update = request.get_json()
    app.logger.debug(f'DEBUG update post: {post_id} {post_to_update}')
    updated_post = posts.update_post(post_id, post_to_update)
    if updated_post is None:
        app.logger.debug(f'DEBUG post update not accepted.')  # Log a message
        return not_found_error("Wrong post format or post not found.")
    else:
        return jsonify(updated_post)


@app.errorhandler(400)
def bad_request(error):
    response = {
        "error": "Bad Request",
        "message": str(error),
        "instructions": API_INSTRUCTIONS
    }
    return jsonify(response), 400


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Bad Request",
        "message": str(error),
        "instructions": API_INSTRUCTIONS
    }), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({
        "error": "Bad Request",
        "message": str(error),
        "instructions": API_INSTRUCTIONS
    }), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
