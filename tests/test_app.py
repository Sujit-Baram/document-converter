from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "document-converter"

def test_txt_to_pdf():
    response = client.post(
        "/convert/txt-to-pdf",
        files={"file": ("sample.txt", b"Hello from Document Converter", "text/plain")},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")

def test_reject_non_txt():
    response = client.post(
        "/convert/txt-to-pdf",
        files={"file": ("sample.docx", b"not really a docx", "application/octet-stream")},
    )
    assert response.status_code == 415
