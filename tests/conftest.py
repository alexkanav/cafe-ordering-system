import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from infrastructure.redis import get_sync_redis_client
from infrastructure.db.base import Base
from infrastructure.db.models.admin import Staff
from infrastructure.db.models.users import User
from domain.core.security import hash_password
from tests.factories.register import make_register_schema


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite://",  # NOT :memory:
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection
    )

    session = TestingSessionLocal()

    # IMPORTANT: allows endpoints that call commit()
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture
def create_staff_user(db_session):
    def _create(**overrides):
        data = make_register_schema(**overrides)
        user = Staff(
            name=data.username,
            email=data.email,
            password=hash_password(data.password),
        )
        db_session.add(user)
        db_session.flush()
        return user

    return _create


@pytest.fixture
def create_client_user(db_session):
    def _create(**overrides):
        user = User(**overrides)
        db_session.add(user)
        db_session.flush()
        return user

    return _create


@pytest.fixture
def redis_client():
    client = get_sync_redis_client()

    yield client

    if client:
        client.close()


@pytest.fixture
def clear_rate_limits(redis_client):
    if redis_client:
        keys = redis_client.keys("LIMITS:LIMITER*")
        if keys:
            redis_client.delete(*keys)


@pytest.fixture
def clear_cache(redis_client):
    if redis_client:
        keys = redis_client.keys("cache:*")
        if keys:
            redis_client.delete(*keys)
