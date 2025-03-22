import backend.backend_app

if __name__ == '__main__':
    app = backend.backend_app.app
    app.run(host="0.0.0.0", port=5002, debug=True)