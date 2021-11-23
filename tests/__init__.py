from flask_testing import TestCase
from Api import create_app, db
# https://pythonhosted.org/Flask-Testing/

TEST_CONFIG = "test"

class BaseTest(TestCase):
    def create_app(self):
        return create_app(TEST_CONFIG)

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        db.create_all()
        try:
            self.populate_db()
        except:
            print('NO DATA INSERTED! missing populate_db function')

    def tearDown(self):
        db.session.remove()
        db.drop_all()


