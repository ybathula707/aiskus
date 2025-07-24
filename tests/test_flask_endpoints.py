import pytest
import logging
from aiskus_app import create_app

logging.basicConfig(level=logging.INFO)

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    #creating test dummpy client to dpendency inject
    #this client will call our endpoints and allow us the test the functions
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_ask_valid(client):
    data = {'question_body': 'Why is the sky blue?'}
    response = client.post('/ask', data=data)
    logging.info(f"response: {response}")
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert "queued" in response.json["message"]

def test_ask_missing_data(client):
    response = client.post('/ask', data={})
    logging.info(f"response: {response}")

    assert response.status_code == 400 or response.json["status"] == "failure"
