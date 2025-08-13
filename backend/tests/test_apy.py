import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

tc = TestClient(app)

@pytest.mark.timeout(10)
def test_chat_stream_endpoint_exists():
    r = tc.post("/api/chat/stream", json={"message": "Hello"})
    assert r.status_code == 200
    # We expect a streamed body; testclient buffers it.
    assert isinstance(r.text, str)