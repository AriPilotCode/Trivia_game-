import pytest
import json
from app.server_multi_tcp import app, create_users_table, get_db

@pytest.fixture(scope='module')
def init_db():
    """Initialize the database before tests run and clean up afterwards."""
    with app.app_context():
        # Create tables and initialize the database
        create_users_table()  # Ensure the table exists
    yield
    # Optionally, you can add teardown logic here if needed

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        yield client