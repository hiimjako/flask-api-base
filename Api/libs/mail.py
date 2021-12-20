import Api
from Api.errors.user import UserInvalidEmail
from flask_mail import Message
from flask import current_app


class Mail:
    """Wrapper for email"""

    EMAIL_DOMAIN = "gmail.com"
    FROM_TITLE = "Stores REST API"
    FROM_EMAIL = f"do-not-reply@{EMAIL_DOMAIN}"

    @classmethod
    def send_email(cls, recipient: list[str], subject: str, text: str, html: str):
        app = current_app
        with app.app_context():
            msg = Message(
                cls.FROM_TITLE + subject,
                sender=cls.FROM_EMAIL,
                recipients=recipient,
            )
            msg.body = text
            msg.html = html
            try:
                Api.mail.send(msg)
            except:  # pragma: no cover
                raise UserInvalidEmail
