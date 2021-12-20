from http import HTTPStatus
from Api.schemas.permission import RoleSchema, RoleModel

from tests import BaseTest


class ModelTest(BaseTest):
    def populate_db(self):
        role_json = {
            "name": "test",
            "priority": 5,
        }
        role: RoleModel = RoleSchema().load(role_json)
        role.save_to_db()

    def test_repr(self) -> None:
        ret = RoleModel.find_by_name("test")
        assert ret.__repr__() == "<Role 'test'>"

    def test_find_by_name(self) -> None:
        ret = RoleModel.find_by_name("test")
        assert ret.id == 4
        assert ret.name == "test"
        assert ret.priority == 5

    def test_delete(self) -> None:
        ret = RoleModel.find_by_name("test")
        ret.delete_from_db()
        ret = RoleModel.find_by_name("test")
        assert ret is None
