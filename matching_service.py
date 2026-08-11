import math
from typing import List
from models import Image, Post
from schemas import MatchResult, ImageResponse

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate the cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
        
    return dot_product / (magnitude1 * magnitude2)

def run_mismatch_guard(post: Post, candidate_image: Image, similarity: float) -> MatchResult:
    """
    The Mismatch Guard: validates if a candidate is a good enough match.
    """
    meta = candidate_image.metadata_info
    
    if not meta:
        return MatchResult(status="REJECTED", reason="Image has no metadata")

    # Rule 1: Confidence threshold
    if meta.confidence < 0.70:
        return MatchResult(
            status="REJECTED", 
            reason=f"AI confidence too low ({meta.confidence}). Not a safe recommendation."
        )
        
    # Rule 2: Similarity threshold
    if similarity < 0.50: # Set somewhat low because of how embeddings cluster
        return MatchResult(
            status="REJECTED", 
            reason=f"Similarity below threshold ({similarity:.2f}). No confident match."
        )
        
    # Rule 3: Category validation
    # If the post explicitly expects a category, check if it matches the detected subject
    if post.expected_category:
        expected = post.expected_category.lower()
        subject = meta.subject.lower()
        if expected not in subject and subject not in expected:
            return MatchResult(
                status="REJECTED",
                reason=f"Category mismatch: expected {post.expected_category}, detected {meta.subject}"
            )
        
    # Passed all rules!
    img_resp = ImageResponse(
        id=candidate_image.id,
        filename=candidate_image.filename,
        created_at=candidate_image.created_at
    )
    
    return MatchResult(
        status="APPROVED",
        image=img_resp,
        similarity_score=similarity
    )
