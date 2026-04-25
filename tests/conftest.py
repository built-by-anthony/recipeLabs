import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from recipeLabs.models import Base


@pytest.fixture
def db_session():
    with PostgresContainer("postgres:16") as postgres:
        engine = create_engine(postgres.get_connection_url())

        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
