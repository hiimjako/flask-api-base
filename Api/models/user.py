from Api.db import db
from Api.libs.mail import Mail
from Api.models.confirmation import ConfirmationModel
from flask import request, url_for
from requests import Response
from werkzeug.security import check_password_hash, generate_password_hash


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("RoleModel", backref=db.backref("user", lazy="dynamic"))

    confirmation = db.relationship(
        "ConfirmationModel",
        lazy="dynamic",
        cascade="all, delete-orphan",
        back_populates="user",
    )

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        # ordered by expiration time (in descending order)
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

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

    def send_confirmation_email(self) -> Response:
        # configure e-mail contents
        subject = "Registration Confirmation"
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        # string[:-1] means copying from start (inclusive) to the last index (exclusive), a more detailed link below:
        # from `http://127.0.0.1:5000/` to `http://127.0.0.1:5000`, since the url_for() would also contain a `/`
        # https://stackoverflow.com/questions/509211/understanding-pythons-slice-notation
        text = f"Please click the link to confirm your registration: {link}"
        html = f"<html>Please click the link to confirm your registration: <a href={link}>link</a></html>"
        # send e-mail with Mail
        return Mail.send_email([self.email], subject, text, html)

    def can(self, permission: str) -> bool:
        return True

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
