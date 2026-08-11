from fastapi.testclient import TestClient
from main import app
from schemas import ImageTags
import pytest

client = TestClient(app)

def test_schema_validation():
    """Test that our Pydantic schema properly validates valid data and rejects bad data"""
    valid_data = {
        "subject": "red fox",
        "category": "animal",
        "attributes": ["wild", "orange"],
        "caption": "A red fox in the snow",
        "confidence": 0.95
    }
    
    # Should not raise exception
    tags = ImageTags(**valid_data)
    assert tags.subject == "red fox"

    # Should raise error missing required fields
    with pytest.raises(ValueError):
        ImageTags(subject="red fox")

def test_mismatch_guard_rejection():
    """Test that the API rejects a post if there is no confident match in the database"""
    # Create a post that we know we don't have images for (e.g. a spaceship)
    response = client.post("/posts", json={
        "content": "A story about a spaceship traveling to Mars.",
        "expected_category": "spaceship"
    })
    assert response.status_code == 200
    post_id = response.json()["id"]

    # Try to find an image for it
    match_response = client.get(f"/posts/{post_id}/images")
    assert match_response.status_code == 200
    data = match_response.json()
    
    # The Mismatch Guard should explicitly reject this because similarity will be low
    assert data["status"] == "REJECTED"
    assert "No embedded images found" in data["reason"] or "Similarity below threshold" in data["reason"] or "Category mismatch" in data["reason"]
