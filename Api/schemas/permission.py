from Api.ma import ma
from Api.models.permission import RoleModel


class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RoleModel
        load_instance = True
        dump_only = ("id",)
