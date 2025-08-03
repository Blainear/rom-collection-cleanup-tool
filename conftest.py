import os
import pytest

@pytest.fixture
def client_id():
    """Provide IGDB client ID via environment variable.

    Skips tests if ``IGDB_CLIENT_ID`` is not set to avoid hard-coding
    credentials in the repository.
    """
    cid = os.environ.get("IGDB_CLIENT_ID")
    if not cid:
        pytest.skip("IGDB_CLIENT_ID not set")
    return cid

@pytest.fixture
def access_token():
    """Provide IGDB access token via environment variable.

    Skips tests if ``IGDB_ACCESS_TOKEN`` is not set.
    """
    token = os.environ.get("IGDB_ACCESS_TOKEN")
    if not token:
        pytest.skip("IGDB_ACCESS_TOKEN not set")
    return token
