import pytest

# Import client fixture from utils to make it available for all tests
from .utils import client  # pyright: ignore[reportUnusedImport] # noqa: F401

@pytest.fixture
def auth_type(request: pytest.FixtureRequest) -> str:
    """Fixture that provides the auth type (user or station) corresponding to the api_key fixture."""
    # Extract the parameter from the api_key fixture
    if hasattr(request, 'node') and hasattr(request.node, 'callspec'):  # type: ignore[misc]
        return request.node.callspec.params.get('api_key', 'user')  # type: ignore[misc]
    return 'user'