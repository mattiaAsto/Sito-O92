from flask_mail import Message

from app.extensions import mail


def send_email(subject, recipients, body, html=None, reply_to=None):
    message = Message(
        subject=subject, recipients=recipients, body=body, html=html, reply_to=reply_to
    )
    mail.send(message)
