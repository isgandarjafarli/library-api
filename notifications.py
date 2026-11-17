"""Notifications for library members.

No real email is sent. MockEmailSender is a mock object: it pretends to send
an email, keeps a list of the messages it "sent", and writes them to
outbox.txt so they can be checked.
"""

OUTBOX_PATH = "outbox.txt"


class MockEmailSender:
    def __init__(self, outbox_path=OUTBOX_PATH):
        self.outbox_path = outbox_path
        self.sent = []

    def send(self, email, subject, body):
        self.sent.append({"to": email, "subject": subject, "body": body})
        with open(self.outbox_path, "a") as f:
            f.write("TO: " + email + " | SUBJECT: " + subject + " | BODY: " + body + "\n")


sender = MockEmailSender()


def send_email(email, subject, body):
    sender.send(email, subject, body)


def book_checked_out(email, title):
    send_email(email, "Book checked out", "You checked out " + title)


def book_returned(email, title, fine):
    send_email(email, "Book returned", "You returned " + title + ". Fine: $" + str(fine))


def loan_renewed(email, title):
    send_email(email, "Loan renewed", "You renewed " + title)


def fine_paid(email, amount):
    send_email(email, "Fine paid", "We received $" + str(amount))
