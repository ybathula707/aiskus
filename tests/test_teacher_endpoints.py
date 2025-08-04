import pytest
import json
from aiskus_app import create_app
from aiskus_app.db import init_db, get_db
import time

#TODO add tests usign dummy data
@pytest.fixture()
def app_test_client():
    app = create_app()
    yield app.test_client()


def test_get_latest_summaries(app_test_client):
    timestamp = int(time.time())
    response = app_test_client.get(f'/get/summaries/latest?timestamp={timestamp}')

    assert response.status_code is 200

    #deserialize and check the the response contents

    response_data = json.loads(response.data)
    assert response_data is not None
    assert response_data["report"] is not None
    assert "themes" in  response_data["report"]

