from Api.db import db
from sqlalchemy import event


class Permission:
    GENERAL = 0
    ADMINISTER = 1


class RoleModel(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    priority = db.Column(db.Integer, unique=True)
    # users = db.relationship("UserModel", backref="role", lazy="dynamic")

    @classmethod
    def find_by_name(cls, name: str) -> "RoleModel":
        return cls.query.filter_by(name=name).first()

    def __repr__(self):
        return "<Role '%s'>" % self.name


# Find better way, doesnt works with flask db upgrade
# maybe better put it into migrations
@event.listens_for(RoleModel.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    db.session.add(RoleModel(name="admin", priority=0))
    db.session.add(RoleModel(name="teacher", priority=1))
    db.session.add(RoleModel(name="student", priority=2))
    db.session.commit()
