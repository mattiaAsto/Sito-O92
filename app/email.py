from flask_mail import Message

from app.extensions import mail


def send_email(subject, recipients, body, html=None):
    message = Message(subject=subject, recipients=recipients, body=body, html=html)
    mail.send(message)
