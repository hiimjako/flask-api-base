from flask_testing import TestCase
from Api import create_app, db, redis_client

# https://pythonhosted.org/Flask-Testing/

TEST_CONFIG = "test"


class BaseTest(TestCase):
    def create_app(self):
        return create_app(TEST_CONFIG, verbose=False)

    def setUp(self):
        self.app = create_app(TEST_CONFIG, verbose=False)
        redis_keys = redis_client.keys()
        # Prevent to flush production redis
        if len(redis_keys) > 0:  # pragma: no cover
            raise SystemExit(
                f"Redis db '{self.app.config['REDIS_DB']}' is not empty (found {len(redis_keys)} keys), exiting"
            )

        db.create_all()
        try:
            self.populate_db()
        except Exception as e:
            # print("NO DATA INSERTED! missing populate_db function")
            # print(e)
            pass

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        redis_client.flushdb()
