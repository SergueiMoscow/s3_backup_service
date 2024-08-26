import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.settings import settings


def get_dsn():
    if 'pytest' in sys.modules:
        return settings.TEST_DB_DSN
    return settings.DB_DSN


db_url = get_dsn()


engine = create_engine(
    url=db_url,
    echo=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"check_same_thread": False},
)


Session = sessionmaker(bind=engine)
session = Session()
