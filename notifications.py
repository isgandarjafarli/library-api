# Mock notifications - no real email gets sent.
# MockEmailSender just remembers what it "sent" and writes it to outbox.txt

OUTBOX_PATH = "outbox.txt"


class MockEmailSender:
    def __init__(self):
        self.sent = []

    def send(self, email, subject, body):
        self.sent.append({"to": email, "subject": subject, "body": body})
        with open(OUTBOX_PATH, "a") as f:
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
