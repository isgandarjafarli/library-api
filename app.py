import os

from flask import Flask, jsonify

from db import init_db
from errors import LibraryError
from routers import book_router, member_router, loan_router, report_router

app = Flask(__name__)

app.register_blueprint(book_router.bp)
app.register_blueprint(member_router.bp)
app.register_blueprint(loan_router.bp)
app.register_blueprint(report_router.bp)


@app.errorhandler(LibraryError)
def handle_library_error(error):
    return jsonify({"error": error.message}), error.status

if not os.path.exists("library.db"):
    init_db()
