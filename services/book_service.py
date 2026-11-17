from errors import bad_request, conflict
from repositories import book_repository
from utils import validation
from utils.checks import require_fields, require_found


def list_books(only_available):
    return book_repository.list_books(only_available)


def get_book(book_id):
    return require_found(book_repository.get_book(book_id), "book not found")


def create_book(data):
    require_fields(data, ["title", "author"], "title and author are required")
    if not validation.is_valid_isbn(data.get("isbn")):
        raise bad_request("invalid isbn")
    return book_repository.create_book(data["title"], data["author"], data["isbn"])



def delete_book(book_id):
    book = get_book(book_id)
    if book["available"] == 0:
        raise conflict("book is on loan")
    book_repository.delete_book(book_id)
