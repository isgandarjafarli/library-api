import db


def list_loans():
    conn = db.connect()
    rows = conn.execute("SELECT * FROM loans").fetchall()
    conn.close()
    return rows

def list_loans_for_member(member_id):
    conn = db.connect()
    rows = conn.execute("SELECT * FROM loans WHERE member_id = ?", (member_id,)).fetchall()
    conn.close()
    return rows


def list_open_loans_with_details():
    conn = db.connect()
    rows = conn.execute(
        """
        SELECT loans.id, books.title, members.name, loans.due_date
        FROM loans
        JOIN books ON books.id = loans.book_id
        JOIN members ON members.id = loans.member_id
        WHERE loans.returned = 0
        """
    ).fetchall()
    conn.close()
    return rows


def get_loan(loan_id):
    conn = db.connect()
    loan = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    conn.close()
    return loan


def create_loan(book_id, member_id, due_date, checked_out):
    conn = db.connect()
    cur = conn.execute(
        "INSERT INTO loans (book_id, member_id, due_date, checked_out) VALUES (?, ?, ?, ?)",
        (book_id, member_id, due_date, checked_out),
    )
    conn.commit()
    loan = conn.execute("SELECT * FROM loans WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return loan


def mark_returned(loan_id, fine):
    conn = db.connect()
    conn.execute("UPDATE loans SET returned = 1, fine = ? WHERE id = ?", (fine, loan_id))
    conn.commit()
    conn.close()


def extend_loan(loan_id, new_due_date):
    conn = db.connect()
    conn.execute(
        "UPDATE loans SET due_date = ?, renewals = renewals + 1 WHERE id = ?",
        (new_due_date, loan_id),
    )
    conn.commit()
    conn.close()


def mark_fine_paid(loan_id):
    conn = db.connect()
    conn.execute("UPDATE loans SET fine_paid = 1 WHERE id = ?", (loan_id,))

    conn.commit()
    conn.close()
