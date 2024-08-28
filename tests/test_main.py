import pytest
import json
from app import app, get_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        yield client


@pytest.fixture
def init_db():
    db = get_db()
    with app.app_context():
        with app.open_resource('schema.sql', mode='r') as f:
            cur = db.cursor()
            cur.execute(f.read())
            db.commit()
            cur.close()
    return db


def test_register(client, init_db):
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b"Registration successful!" in response.data

    # Test registration with an existing username
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 400
    assert b"Username already exists" in response.data


def test_login(client):
    # Register a user first
    client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })

    # Test login with correct credentials
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b"Login successful!" in response.data

    # Test login with incorrect credentials
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_get_question(client):
    # Register and login a user first
    client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })

    # Set difficulty and category in session
    client.post('/submit_selection', json={
        'difficulty': 'easy',
        'category': 'General Knowledge'
    })

    # Test getting a question
    response = client.get('/question')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'question' in data


def test_submit_answer(client):
    # Register and login a user first
    client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })

    # Set difficulty and category in session
    client.post('/submit_selection', json={
        'difficulty': 'easy',
        'category': 'General Knowledge'
    })

    # Get a question to answer
    response = client.get('/question')
    assert response.status_code == 200
    data = json.loads(response.data)
    question_key = data['question']['key']
    correct_answer = data['question']['answers'][0]  # Assume first answer is correct

    # Test submitting a correct answer
    response = client.post('/submit_answer', json={
        'username': 'testuser',
        'questionKey': question_key,
        'answer': correct_answer
    })
    assert response.status_code == 200
    assert b"Correct answer" in response.data

    # Test submitting an incorrect answer
    response = client.post('/submit_answer', json={
        'username': 'testuser',
        'questionKey': question_key,
        'answer': 'Incorrect answer'
    })
    assert response.status_code == 200
    assert b"Incorrect answer" in response.data

