import pytest
from app import app
from db import init_db, clear_people

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup before each test
    init_db()
    clear_people()
    yield
    # Teardown after each test
    clear_people()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_get_people_empty(client):
    rv = client.get('/api/people')
    assert rv.status_code == 200
    assert rv.json == []


def test_create_person(client):
    data = {'name': 'Test', 'surname': 'User'}
    rv = client.post('/api/people', json=data)
    assert rv.status_code == 201
    j = rv.json
    assert 'id' in j
    assert j['name'] == 'Test'
    assert j['surname'] == 'User'


def test_clear_people(client):
    client.post('/api/people', json={'name': 'A', 'surname': 'B'})
    rv = client.delete('/api/people')
    assert rv.status_code == 200
    rv2 = client.get('/api/people')
    assert rv2.json == []


def test_draw_assignments(client):
    # Need at least 2 people
    client.post('/api/people', json={'name': 'Alice', 'surname': 'Smith'})
    client.post('/api/people', json={'name': 'Bob', 'surname': 'Jones'})
    rv = client.post('/api/draw')
    assert rv.status_code == 200
    assert rv.json['status'] == 'drawn'
    assert rv.json['count'] == 2
