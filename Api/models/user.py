import json
from time import time

import Api.errors.token as TokenException
from Api.db import db, redis_client
from Api.libs.mail import Mail
from Api.models.permission import DEFAULT_ROLE, Permission
from authlib.jose import JsonWebSignature
from flask import current_app, request, url_for
from requests import Response
from werkzeug.security import check_password_hash, generate_password_hash

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

    def generate_external_token(
        self, expiration=CONFIRMATION_EXPIRATION_DELTA
    ) -> "bytes":
        """Generate a token to be used in external envs, can be used only one time"""
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
            raise TokenException.Create

    @classmethod
    def user_by_token(cls, token) -> "UserModel":
        """Validate a confirmation token for invite, it returns the user if the token is valid. After invalidates the token"""

        if redis_client.get(f"external_token:{token}") is not None:
            raise TokenException.AlreadyUsed

        try:
            secret = bytes(
                current_app.config["SECRET_KEY"], encoding="raw_unicode_escape"
            )
            jws = JsonWebSignature()
            data = jws.deserialize_compact(token, secret)
            payload = json.loads(data["payload"])
            redis_client.set(
                f"external_token:{token}",
                "",
                ex=payload["expiration"],
            )
        except Exception as e:
            raise TokenException.BadSignature

        if time() > payload.get("expiration"):
            raise TokenException.Expired

        user = cls.find_by_id(payload.get("user_id"))

        return user

    def send_confirmation_email(self) -> Response:
        # configure e-mail contents
        subject = "Registration Confirmation"
        link = request.url_root[:-1] + url_for(
            "confirmation",
            confirmation_token=self.generate_external_token(),
        )
        # string[:-1] means copying from start (inclusive) to the last index (exclusive), a more detailed link below:
        # from `http://127.0.0.1:5000/` to `http://127.0.0.1:5000`, since the url_for() would also contain a `/`
        # https://stackoverflow.com/questions/509211/understanding-pythons-slice-notation
        text = f"Please click the link to confirm your registration: {link}"
        html = f"<html>Please click the link to confirm your registration: <a href={link}>link</a></html>"
        # send e-mail with Mail
        return Mail.send_email([self.email], subject, text, html)

    def send_reset_password_email(self) -> Response:
        # configure e-mail contents
        subject = "Password reset request"
        link = request.url_root[:-1] + url_for(
            "usercredentialsexternal",
            reset_token=self.generate_external_token(),
        )
        text = f"""Hi there,
        Looks like a request was made to reset the password for your {self.username} account.
        You can reset your password using the link below:
        {link}
        If you didn’t want to reset your password, you can safely ignore this email."""

        html = f"""<html>Hi there,<br/>
        Looks like a request was made to reset the password for your {self.username} account.
        You can reset your password using the link below:<br/>
        <a href={link}>link</a><br/>
        If you didn’t want to reset your password, you can safely ignore this email.</html>"""

        # send e-mail with Mail
        return Mail.send_email([self.email], subject, text, html)

    def can(self, permission: int) -> bool:
        if self.role.priority == Permission.ADMINISTER:
            return True
        return permission == self.role.priority

    def save_user_and_update_password(self) -> None:
        self.hash_password()
        self.save_to_db()
        from Api.jwt import delete_all_refresh_token_by_user_id

        delete_all_refresh_token_by_user_id(self.id)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<User ('{self.username}', '{self.email}')>"
