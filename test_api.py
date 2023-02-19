from fastapi import FastAPI
import pytest
import schemathesis
from starlette_testclient import TestClient

from api import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def web_schema(client):
    openapi = client.app.openapi()
    return schemathesis.from_dict(openapi)


schema = schemathesis.from_pytest_fixture("web_schema")


@schema.parametrize()
def test_app(case, client):
    case.call_and_validate(session=client)
