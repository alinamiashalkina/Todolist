from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from constants import DB_CONNECTION
from contextlib import contextmanager


engine = create_engine(
    "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
        **DB_CONNECTION)
)


Session = sessionmaker(bind=engine)


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


