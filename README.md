# AI Image Understanding & Content Matching Engine

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-1.5_Flash-orange.svg)
![Pydantic](https://img.shields.io/badge/Pydantic-V2-purple.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)

## 📌 Project Overview

This repository contains the backend implementation for an **AI Image Understanding & Content Matching Engine**. It was built as a capstone project to demonstrate the ability to construct a reliable, production-grade AI pipeline that can gracefully handle the inherent unreliability of Large Language Models and Vision APIs.

At its core, the system processes a raw image library using **Vision AI** to generate strict, structured metadata. It then uses **Vector Embeddings** to mathematically rank and match the most relevant images to incoming text content (like blog posts).

The crown jewel of this system is the **Mismatch Guard**—a multi-layered safety net that evaluates AI confidence, cosine similarity scores, and categorical alignment to aggressively prevent and explain incorrect image recommendations (e.g., stopping the system from suggesting a visually similar wolf image for an article specifically about red foxes).

---

## 🏗️ Architecture & Data Flow

The system is built on an asynchronous, decoupled architecture separating the slow AI ingestion tasks from the fast client-facing matching API.

```text
======================= BATCH INGESTION PIPELINE =======================
Images ─(async batch job)─► Gemini Vision API 
                            │
                            ├─► Validated via Pydantic Schema
                            ├─► {tags, category, caption, confidence} ─► SQLite DB
                            └─► embed(caption + tags) ─────────► image_vectors

======================= CLIENT MATCHING API ============================
Posts ──────────────► embed(post text) ─────────────────────────────► post_vectors

GET /posts/:id/images
 ├─► 1. Cosine Similarity Ranking (image_vectors × post_vectors)
 ├─► 2. Mismatch Guard Evaluation:
 │      - Is AI confidence > 70%?
 │      - Is Cosine Similarity > 50%?
 │      - Does the Expected Category match the Detected Subject?
 │
 ├─► [PASS] ─► Returns Suggested Image (status: "APPROVED")
 │
 └─► [FAIL] ─► Returns Human-Readable Reason (status: "REJECTED")

======================= HUMAN-IN-THE-LOOP ==============================
Review API: 
POST /suggestions/:id/approve  |  POST /suggestions/:id/reject
```

---

## ✨ Core Features & Technical Achievements

### 1. 🛡️ Schema Validation & "Never Trust the AI"
Raw LLM text outputs are highly unpredictable. This system forces the Gemini Vision model to respond in a strict JSON format, which is immediately intercepted and validated using a rigid **Pydantic schema**. Invalid shapes or hallucinations are explicitly caught before they can poison the database.

### 2. ⏱️ Resilient Background Batch Processing
Vision AI calls are slow and prone to rate limits. Image ingestion is moved entirely off the main thread using FastAPI's `BackgroundTasks`. The ingestion loop includes:
- Idempotent processing (skipping already tagged images).
- Exponential backoff and retry logic for API failures.
- **Cost Tracking**: The API tracks and records the exact simulated token cost incurred per processed image.

### 3. 🧠 Semantic Matching via Vector Embeddings
Instead of relying on fragile keyword searches, the engine passes both the image tags and the blog post content through the `text-embedding-004` model. The high-dimensional vectors are then compared mathematically using **Cosine Similarity**, allowing the system to understand that "vulpes vulpes" and "red fox" mean the exact same thing.

### 4. 🛑 The Mismatch Guard
A critical safety layer designed to make the AI reliable for production. It explicitly refuses to make a suggestion if the math or the logic doesn't add up, preventing embarrassing AI failures. It evaluates:
*   **Confidence:** Rejects matches if the initial vision scan was uncertain.
*   **Thresholding:** Rejects matches if the vector distance is too far.
*   **Categorical Alignment:** Explicitly cross-references the expected subject against the detected subject.

### 5. 🧑‍💻 Human-in-the-Loop Review API
The AI makes suggestions, but a human has the final say. Approved matches from the guard generate a "pending" suggestion in the database, which can be permanently finalized or discarded via dedicated `/suggestions/{id}/approve` and `reject` endpoints.

---

## 🚀 Setup & Local Installation

### Prerequisites
- Python 3.10+
- A Google Gemini API Key (Free Tier is perfectly fine)

### 1. Clone the repository
```bash
git clone https://github.com/mianhasssan/Capstone-image-relevance.git
cd Capstone-image-relevance
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Rename the `.env.example` file to `.env` and insert your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./capstone.db
```

### 4. Run the API Server
Start the FastAPI application using Uvicorn:
```bash
uvicorn main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

---

## 📖 API Usage Guide

Once the server is running, navigate to the auto-generated Swagger documentation at **[http://localhost:8000/docs](http://localhost:8000/docs)** to test the endpoints interactively.

### The Standard Workflow:
1. **Ingest Images:** 
   Hit `POST /images/process-batch` to trigger the background worker. Watch your terminal to see Gemini successfully tagging the local seed images and generating vectors.
2. **View the Database:** 
   Hit `GET /images` to see the parsed subjects and filenames saved to your database.
3. **Create Content:** 
   Hit `POST /posts` with a JSON payload representing a new article (e.g., `{"content": "A story about a red fox in the wild.", "expected_category": "red fox"}`).
4. **Trigger the Matching Engine:** 
   Copy the ID of the post you just created, and hit `GET /posts/{post_id}/images`. 
   *   Watch it return a successful match for the fox!
   *   *Test the Guard:* Create a post expecting a "wolf", and watch the system safely `REJECT` the fox image with a clear explanation!
5. **Human Review:** 
   Take the `suggestion_id` returned from a successful match and POST it to `/suggestions/{id}/approve` to finalize the workflow.

---

## 🧪 Automated Testing
The system includes an automated test suite written with `pytest` to guarantee the integrity of the Mismatch Guard and the Pydantic schema validation.

To run the tests:
```bash
pytest test_engine.py
```
