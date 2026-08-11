# AI Image Understanding & Content Matching Engine - Design Doc

## 1. The Problem
We need to build a system that can understand a library of images, tag them with structured metadata (subjects, categories, attributes, captions), and match the most contextually relevant image to a given blog post. 

Critically, the system must employ a **mismatch guard**: it should confidently recommend good matches, but gracefully refuse bad matches (e.g., rejecting a wolf image for a red fox article) with a clear, human-readable explanation.

## 2. Explicit Non-Goal
- We are **not** building a massive production image platform or a complex frontend UI. The system is scoped to ~50 images, and the "review interface" will be simple API endpoints.

## 3. Data Model (Database Design)
We will use **PostgreSQL** (with the `pgvector` extension for embeddings).

### Tables:
*   `images`: Stores the raw images or image URLs.
    *   `id` (UUID, PK)
    *   `filename` / `url` (String)
    *   `created_at` (Timestamp)
*   `image_metadata`: Stores the structured output from the Vision AI.
    *   `image_id` (UUID, FK)
    *   `subject` (String)
    *   `category` (String)
    *   `attributes` (JSONB / Array of Strings)
    *   `caption` (String)
    *   `confidence` (Float)
*   `embeddings`: Stores the vector embeddings for semantic search.
    *   `id` (UUID, PK)
    *   `reference_type` (Enum: 'image', 'post')
    *   `reference_id` (UUID)
    *   `vector` (Vector)
*   `posts`: Stores the blog posts we want to match images against.
    *   `id` (UUID, PK)
    *   `content` (Text)

## 4. Image Metadata Schema (Zod/Pydantic)
When we query the Vision Model (e.g., Gemini Flash), we will enforce this structured JSON response:

```json
{
  "subject": "red fox",
  "category": "animal",
  "attributes": ["orange fur", "wild", "forest"],
  "caption": "A red fox standing in a forest",
  "confidence": 0.94
}
```

## 5. API Surface
*   `POST /images/process` (Background Job): Triggers the vision processing and embedding generation for a batch of images.
*   `GET /posts/:id/images`: The core matching endpoint. Returns ranked image suggestions.
*   `POST /suggestions/:id/approve`: Human-in-the-loop review endpoint.
*   `POST /suggestions/:id/reject`: Human-in-the-loop review endpoint.

## 6. Matching Strategy & Guard Rules
1.  **Similarity Search:** Both image captions and blog post texts are converted to vectors (embeddings). We use cosine similarity to rank the closest image vectors to a given post vector.
2.  **The Mismatch Guard:** Before returning the top match, we check:
    *   **Confidence Threshold:** Was the vision model confident in its initial tags? (e.g., `confidence > 0.8`).
    *   **Semantic Threshold:** Is the cosine similarity score above a strict baseline?
    *   **Category Validation:** Does the detected subject logically align with the post's core topic?
    *   **Fallback:** If the guard fails, the system returns `"No confident match"` along with a human-readable reason (e.g., `"Animal category mismatch: expected fox, detected wolf"`).
