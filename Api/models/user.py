import json
from Api.db import db
from Api.libs.mail import Mail
from flask import request, url_for, current_app
from requests import Response
from werkzeug.security import check_password_hash, generate_password_hash
from authlib.jose import JsonWebSignature
from time import time
import Api.errors.confirmation as ConfirmationException


from Api.models.permission import DEFAULT_ROLE, Permission

CONFIRMATION_EXPIRATION_DELTA = 1800  # 30 minutes
HEADER_TOKEN = {"alg": "HS256"}


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    avatar = db.Column(db.String(80), nullable=True, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(
        db.Integer, db.ForeignKey("roles.id"), nullable=False, default=DEFAULT_ROLE
    )
    role = db.relationship("RoleModel", backref=db.backref("user", lazy="dynamic"))

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def hash_password(self):
        self.password = generate_password_hash(self.password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_confirmation_token(
        self, expiration=CONFIRMATION_EXPIRATION_DELTA
    ) -> "bytes":
        """Generate a confirmation token for invite"""
        try:
            jws = JsonWebSignature()
            payload = {
                "user_id": self.id,
                "expiration": int(time()) + expiration,
            }
            payload = f"{json.dumps(payload)}"
            payload = bytes(payload, encoding="raw_unicode_escape")
            secret = bytes(
                current_app.config["SECRET_KEY"], encoding="raw_unicode_escape"
            )
            return jws.serialize_compact(HEADER_TOKEN, payload, secret)
        except:
            raise ConfirmationException.ConfirmationCreate

    @classmethod
    def user_by_token(cls, token) -> "UserModel":
        """Validate a confirmation token for invite, it returns the user if the token is valid"""
        try:
            secret = bytes(
                current_app.config["SECRET_KEY"], encoding="raw_unicode_escape"
            )
            jws = JsonWebSignature()
            data = jws.deserialize_compact(token, secret)
            payload = json.loads(data["payload"])
        except:
            raise ConfirmationException.BadSignature

        if time() > payload.get("expiration"):
            raise ConfirmationException.ConfirmationExpired

        user = cls.find_by_id(payload.get("user_id"))

        return user

    def send_confirmation_email(self) -> Response:
        # configure e-mail contents
        subject = "Registration Confirmation"
        link = request.url_root[:-1] + url_for(
            "confirmation",
            confirmation_token=self.generate_confirmation_token(),
        )
        # string[:-1] means copying from start (inclusive) to the last index (exclusive), a more detailed link below:
        # from `http://127.0.0.1:5000/` to `http://127.0.0.1:5000`, since the url_for() would also contain a `/`
        # https://stackoverflow.com/questions/509211/understanding-pythons-slice-notation
        text = f"Please click the link to confirm your registration: {link}"
        html = f"<html>Please click the link to confirm your registration: <a href={link}>link</a></html>"
        # send e-mail with Mail
        return Mail.send_email([self.email], subject, text, html)

    def can(self, permission: int) -> bool:
        if self.role.priority == Permission.ADMINISTER:
            return True
        return permission == self.role.priority

    def save_user_and_update_password(self) -> None:
        self.hash_password()
        db.session.add(self)
        db.session.commit()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
