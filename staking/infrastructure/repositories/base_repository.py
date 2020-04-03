from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from staking.config import NETWORK, NETWORK_ID

engine = create_engine(
    f"{NETWORK['db']['DB_DRIVER']}://{NETWORK['db']['DB_USER']}:"
    f"{NETWORK['db']['DB_PASSWORD']}"
    f"@{NETWORK['db']['DB_HOST']}:"
    f"{NETWORK['db']['DB_PORT']}/{NETWORK['db']['DB_NAME']}", echo=False)

Session = sessionmaker(bind=engine)
default_session = Session()


class BaseRepository:

    def __init__(self):
        self.session = default_session

    def add_item(self, item):
        try:
            self.session.add(item)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        self.session.commit()

    def add_all_items(self, items):
        try:
            self.session.add_all(items)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
