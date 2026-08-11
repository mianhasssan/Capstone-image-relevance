# AI Image Understanding & Content Matching Engine

This repository contains the backend implementation for an **AI Image Understanding & Content Matching Engine**. It processes raw images using Vision AI, generates strict structured metadata, and uses vector embeddings to mathematically match the most relevant images to blog posts. 

A core feature of this system is the **Mismatch Guard**, a production-grade safety layer that evaluates AI confidence, cosine similarity, and categorical alignment to aggressively prevent and explain incorrect image recommendations.

## 🏗️ Architecture Overview

```text
Images ─(batch job)─► Gemini Vision API ─► {tags, caption, confidence} ─► image_metadata
 └─► embed(caption) ────────► image_vectors

Posts ──────────────► embed(post text) ─────────────────────────────► post_vectors

GET /posts/:id/images
 └─► Cosine Similarity Ranking (image_vectors × post_vectors)
 └─► Mismatch Guard (category check + threshold + confidence)
 ├─► Suggested image (ranked, explained)
 └─► "No good match" + explanation
 └─► Review API: approve / reject
```

## ✨ Core Features
- **Schema Validation**: Uses Pydantic to strictly enforce that the Gemini LLM returns valid, predictable JSON.
- **Resilient Batch Processing**: Background tasks iterate over images, auto-retry on API failures, and accurately track simulated API costs.
- **Semantic Matching**: Converts images and posts to vector embeddings and ranks them using Cosine Similarity.
- **The Mismatch Guard**: Safely intercepts bad matches (e.g., refusing to suggest a wolf for a fox article).
- **Human-in-the-Loop Review**: Dedicated `/suggestions` API to manually approve or reject the AI's final pairings.

## 🚀 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup:**
   Rename `.env.example` to `.env` and insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the API:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Run the Automated Tests:**
   ```bash
   pytest test_engine.py
   ```

## 📖 API Usage
Once the server is running, visit `http://localhost:8000/docs` to use the interactive Swagger UI.

1. `POST /images/process-batch` - Triggers the background job to run AI vision processing on the `images/` directory.
2. `POST /posts` - Create a new blog post.
3. `GET /posts/{post_id}/images` - Ask the matching engine to find the best image (triggers the mismatch guard).
4. `POST /suggestions/{id}/approve` - Human approval of a suggested match.
