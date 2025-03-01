from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_pdf():
    response = client.post("/upload/", files={"file": ("test.pdf", b"fakepdfcontent")})
    assert response.status_code == 200


def test_upload_docx():
    response = client.post("/upload/", files={"file": ("test.docx", b"fakedocxcontent")})
    assert response.status_code == 200


def test_websocket():
    with client.websocket_connect("/query/") as websocket:
        websocket.send_text("Find candidates with Python skills")
        response = websocket.receive_text()
        assert "Python" in response
