import pytest

@pytest.fixture(params=["stream", "no-stream"])
def stream_enabled(request):
    """Should streaming be enabled for this test ?"""
    if request.param == "stream":
        return True
    elif request.param == "no-stream":
        return False
    else:
        raise ValueError(f"Unknown api_key type: {request.param}")
    