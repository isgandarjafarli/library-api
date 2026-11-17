from flask import Blueprint, jsonify, request

from services import loan_service
from utils.fines import money

bp = Blueprint("loans", __name__)


def loan_json(loan):
    return {
        "id": loan["id"],
        "book_id": loan["book_id"],
        "member_id": loan["member_id"],
        "due_date": loan["due_date"],
        "returned": bool(loan["returned"]),
        "fine": money(loan["fine"]),
        "fine_paid": bool(loan["fine_paid"]),
        "renewals": loan["renewals"],
        "checked_out": loan["checked_out"],
    }


@bp.route("/loans", methods=["GET"])
def list_loans():
    only_overdue = request.args.get("overdue") == "true"
    result = []
    for loan in loan_service.list_loans(only_overdue):
        item = loan_json(loan)
        item["current_fine"] = money(loan_service.current_fine(loan))
        result.append(item)
    return jsonify(result)


@bp.route("/loans/<int:loan_id>", methods=["GET"])
def get_loan(loan_id):
    loan = loan_service.get_loan(loan_id)
    item = loan_json(loan)
    item["current_fine"] = money(loan_service.current_fine(loan))
    return jsonify(item)

@bp.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json(silent=True) or {}
    loan = loan_service.create_loan(data)
    return jsonify(loan_json(loan)), 201


@bp.route("/loans/<int:loan_id>/return", methods=["POST"])
def return_book(loan_id):
    loan = loan_service.return_book(loan_id)
    return jsonify(loan_json(loan))


@bp.route("/loans/<int:loan_id>/renew", methods=["POST"])
def renew_loan(loan_id):
    loan = loan_service.renew_loan(loan_id)
    return jsonify(loan_json(loan))

@bp.route("/loans/<int:loan_id>/pay-fine", methods=["POST"])
def pay_fine(loan_id):
    loan = loan_service.pay_fine(loan_id)
    return jsonify(loan_json(loan))
