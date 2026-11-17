from errors import bad_request, conflict
from repositories import loan_repository, member_repository
from services import loan_service
from utils import validation
from utils.checks import require_fields, require_found


def list_members():
    return member_repository.list_members()


def get_member(member_id):
    return require_found(member_repository.get_member(member_id), "member not found")


def create_member(data):
    require_fields(data, ["name"], "name is required")
    if not validation.is_valid_email(data.get("email")):
        raise bad_request("invalid email")
    member_type = data.get("type", "student")
    if not validation.is_valid_member_type(member_type):
        raise bad_request("type must be student or staff")
    if member_repository.get_member_by_email(data["email"]) is not None:
        raise conflict("email already registered")
    return member_repository.create_member(data["name"], data["email"], member_type)


def member_account(member_id):
    """Return the member's loans, how much they owe and how many loans they have left."""
    member = get_member(member_id)
    loans = loan_repository.list_loans_for_member(member_id)
    remaining = loan_service.loan_limit(member) - loan_service.count_open_loans(loans)
    return loans, loan_service.total_owed(loans), remaining
