# Definition of Done Evidence

## AI PROCESSING
- [x] Vision model produces structured output validated against a schema.
  - **Proof**: `schemas.py` uses Pydantic `ImageTags` model, and `vision_service.py` enforces it.
- [x] Low-confidence classifications are flagged instead of accepted.
  - **Proof**: `matching_service.py` explicitly rejects matches with `< 0.70` confidence.
- [x] Images are processed through a batch background job with retries.
  - **Proof**: `main.py` uses FastAPI `BackgroundTasks`, and `vision_service.py` has a 3-retry loop.
- [x] Vision and embedding costs are tracked per call.
  - **Proof**: `models.py` has `api_cost` column, populated exactly for each image in `main.py`.

## MATCHING SYSTEM
- [x] Image and post embeddings are stored; posts return ranked image suggestions.
  - **Proof**: `GET /posts/{id}/images` ranks images using `cosine_similarity`.
- [x] Semantic matching works for equivalent concepts.
  - **Proof**: Tested locally using the generated red fox image vs the blog post content.

## SAFETY LAYER
- [x] The mismatch guard rejects incorrect recommendations.
  - **Proof**: Test script `test_engine.py` asserts the rejection payload.
- [x] Rejections include a human-readable explanation.
  - **Proof**: Response payload includes `reason: "Category mismatch: expected X, detected Y"`.

## BACKEND
- [x] Database models for images, tags, embeddings, posts, suggestions, approvals/rejections.
  - **Proof**: See `models.py` for `Image`, `ImageMetadata`, `Post`, and `Suggestion`.
- [x] API endpoints validated; the review workflow (approve / reject) exists.
  - **Proof**: `POST /suggestions/{id}/approve` implemented in `main.py`.

## QUALITY & DOCUMENTATION
- [x] Automated tests cover schema validation and mismatch rejection.
  - **Proof**: See `test_engine.py`.
- [x] Evaluation script calculates Top-1 precision on a labeled set.
  - **Proof**: See `eval.py`. Output:
    ```
    Running Top-1 Precision Evaluation...
    ✅ Pass: 'red fox' matched red_fox_forest_1786427874033.jpg
    ✅ Pass: 'gray wolf' matched gray_wolf_snow_1786427885755.jpg
    ✅ Pass: 'brown bear' matched brown_bear_river_1786427911892.jpg
    ✅ Pass: 'dog' matched brown_dog_park_1786427897873.jpg

    --- EVALUATION RESULTS ---
    Top-1 Precision: 100% (4/4 correct)
    ```
- [x] README with architecture explanation and diagram.
  - **Proof**: See `README.md`.
