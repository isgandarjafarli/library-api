from datetime import date, timedelta

import notifications
from errors import bad_request, conflict
from repositories import book_repository, loan_repository, member_repository
from utils import fines, validation
from utils.checks import require_fields, require_found

LOAN_DAYS = 14
STUDENT_LOAN_LIMIT = 3
STAFF_LOAN_LIMIT = 5
MAX_RENEWALS = 1


# helpers (members and reports use these too)

def loan_limit(member):
    if member["type"] == "staff":
        return STAFF_LOAN_LIMIT
    return STUDENT_LOAN_LIMIT


def current_fine(loan):
    if loan["returned"] == 0:
        return fines.fine_for(loan["due_date"])
    return loan["fine"]

def amount_owed(loan):
    if loan["returned"] == 0:
        return fines.fine_for(loan["due_date"])
    if loan["fine_paid"] == 0:
        return loan["fine"]
    return 0


def total_owed(loans):
    total = 0
    for loan in loans:
        total += amount_owed(loan)
    return total


def count_open_loans(loans):
    count = 0
    for loan in loans:
        if loan["returned"] == 0:
            count += 1
    return count


def is_overdue(loan):
    return loan["returned"] == 0 and fines.days_late(loan["due_date"]) > 0



# loan actions

def list_loans(only_overdue):
    loans = loan_repository.list_loans()
    if not only_overdue:
        return loans
    result = []
    for loan in loans:
        if is_overdue(loan):
            result.append(loan)
    return result


def get_loan(loan_id):
    return require_found(loan_repository.get_loan(loan_id), "loan not found")


def create_loan(data):
    require_fields(data, ["book_id", "member_id"], "book_id and member_id are required")
    if data.get("due_date") and not validation.is_valid_date(data["due_date"]):
        raise bad_request("invalid due_date")

    book = require_found(book_repository.get_book(data["book_id"]), "book not found")
    member = require_found(member_repository.get_member(data["member_id"]), "member not found")
    if book["available"] == 0:
        raise conflict("book is not available")

    # no new loans if they owe money or are at the limit
    member_loans = loan_repository.list_loans_for_member(member["id"])
    if total_owed(member_loans) > 0:
        raise conflict("member has unpaid fines")
    if count_open_loans(member_loans) >= loan_limit(member):
        raise conflict("loan limit reached")

    today = date.today()
    due_date = data.get("due_date") or (today + timedelta(days=LOAN_DAYS)).isoformat()
    loan = loan_repository.create_loan(book["id"], member["id"], due_date, today.isoformat())
    book_repository.set_available(book["id"], False)

    notifications.book_checked_out(member["email"], book["title"])
    return loan


def return_book(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 1:
        raise conflict("loan already returned")

    fine = fines.fine_for(loan["due_date"])
    loan_repository.mark_returned(loan_id, fine)
    book_repository.set_available(loan["book_id"], True)

    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    notifications.book_returned(member["email"], book["title"], fines.money(fine))
    return loan_repository.get_loan(loan_id)


def renew_loan(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 1:
        raise conflict("loan already returned")
    if date.fromisoformat(loan["due_date"]) < date.today():
        raise conflict("overdue loans cannot be renewed")
    if loan["renewals"] >= MAX_RENEWALS:
        raise conflict("loan was already renewed")

    new_due = (date.fromisoformat(loan["due_date"]) + timedelta(days=LOAN_DAYS)).isoformat()
    loan_repository.extend_loan(loan_id, new_due)

    member = member_repository.get_member(loan["member_id"])
    book = book_repository.get_book(loan["book_id"])
    notifications.loan_renewed(member["email"], book["title"])
    return loan_repository.get_loan(loan_id)


def pay_fine(loan_id):
    loan = get_loan(loan_id)
    if loan["returned"] == 0:
        raise conflict("return the book before paying")
    if loan["fine"] <= 0 or loan["fine_paid"] == 1:
        raise conflict("no fine to pay")

    loan_repository.mark_fine_paid(loan_id)

    member = member_repository.get_member(loan["member_id"])
    notifications.fine_paid(member["email"], fines.money(loan["fine"]))
    return loan_repository.get_loan(loan_id)
