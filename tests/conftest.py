"""Pytest configuration and shared fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provides a TestClient instance for making requests to the app.
    Fresh app instance per test ensures test isolation.
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Sample student email for testing."""
    return "testStudent@mergington.edu"


@pytest.fixture
def sample_activity():
    """Sample activity name that exists in the app."""
    return "Chess Club"


@pytest.fixture
def new_student_email():
    """Email of a student not yet registered in sample activities."""
    return "newStudent@mergington.edu"
