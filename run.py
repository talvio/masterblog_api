import backend.backend_app

if __name__ == '__main__':
    """ Treats backend_app as a real module. Starts the Flask app here. """
    app = backend.backend_app.app
    app.run(host="0.0.0.0", port=5002, debug=True)