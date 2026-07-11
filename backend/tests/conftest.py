import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:?check_same_thread=False"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Import all models to ensure they are registered with Base.metadata
    import app.models
    from app.limiter import limiter
    Base.metadata.create_all(bind=engine)
    # Disable rate limiting for the test session so sequential calls don't hit IP limits
    limiter.enabled = False
    yield
    limiter.enabled = True
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Overwrite get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    # Clean up and rollback transaction so tests are isolated
    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()
