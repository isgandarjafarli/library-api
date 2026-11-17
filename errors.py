class LibraryError(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status


# make an error with any message and status code
def error(message, status):
    return LibraryError(message, status)

def bad_request(message):
    return error(message, 400)


def not_found(message):
    return error(message, 404)

def conflict(message):
    return error(message, 409)
