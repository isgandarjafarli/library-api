from flask import jsonify


class LibraryError(Exception):
    """An error that should be sent back to the client as JSON."""

    def __init__(self, message, status):
        super().__init__(message)
        self.message = message
        self.status = status


def error(message, status):
    """Create an error with a custom message and HTTP status code."""
    return LibraryError(message, status)


def bad_request(message):
    return error(message, 400)


def not_found(message):
    return error(message, 404)


def conflict(message):
    return error(message, 409)


def register_error_handlers(app):
    @app.errorhandler(LibraryError)
    def handle_library_error(err):
        return jsonify({"error": err.message}), err.status
