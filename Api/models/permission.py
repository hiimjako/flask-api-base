from Api.db import db
from sqlalchemy import event


class Permission:
    ADMINISTER = 0
    TEACHER = 1
    STUDENT = 2


DEFAULT_ROLE = Permission.STUDENT


class RoleModel(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # is useless priority?
    priority = db.Column(db.Integer, unique=True)
    # users = db.relationship("UserModel", backref="role", lazy="dynamic")

    @classmethod
    def find_by_name(cls, name: str) -> "RoleModel":
        return cls.query.filter_by(name=name).first()

    def __repr__(self):
        return "<Role '%s'>" % self.name


# Find better way, doesnt works with flask db upgrade
# maybe better put it into migrations
# TODO: move into migrations
@event.listens_for(RoleModel.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    db.session.add(RoleModel(name="admin", priority=Permission.ADMINISTER))
    db.session.add(RoleModel(name="teacher", priority=Permission.TEACHER))
    db.session.add(RoleModel(name="student", priority=Permission.STUDENT))
    db.session.commit()
