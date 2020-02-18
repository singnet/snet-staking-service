from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from staking.config import NETWORKS, NETWORK_ID

engine = create_engine(
    f"{NETWORKS['db']['DB_DRIVER']}://{NETWORKS['db']['DB_USER']}:"
    f"{NETWORKS['db']['DB_PASSWORD']}"
    f"@{NETWORKS['db']['DB_HOST']}:"
    f"{NETWORKS['db']['DB_PORT']}/{NETWORKS['db']['DB_NAME']}", echo=False)

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
