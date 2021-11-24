import os
from typing import List

import Api
from Api.libs.env import get_env_path
from Api.libs.strings import gettext
from flask_mail import Message
from flask import render_template


class Mail:
    """Wrapper for email"""

    EMAIL_DOMAIN = "gmail.com"
    FROM_TITLE = "Stores REST API"
    FROM_EMAIL = f"do-not-reply@{EMAIL_DOMAIN}"

    @classmethod
    def send_email(cls, recipient, subject, template):
        app = Api.create_app(get_env_path("FLASK_ENV"))
        with app.app_context():
            msg = Message(
                cls.FROM_TITLE + subject,
                sender=cls.FROM_EMAIL,
                recipients=[recipient],
            )
            msg.body = render_template(template + ".txt")
            msg.html = render_template(template + ".html")
            Api.mail.send(msg)
