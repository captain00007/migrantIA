import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


def test_home_view_renders_successfully(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200
    assert "MigrantIA" in response.content.decode("utf-8")
    assert "manifest.json" in response.content.decode("utf-8")
    assert "lang-selector" in response.content.decode("utf-8")
    assert "Kreyòl" in response.content.decode("utf-8")
