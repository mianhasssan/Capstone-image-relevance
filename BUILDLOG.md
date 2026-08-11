# AI Usage Log

## Where AI Helped
I used an AI assistant heavily during the architecture and implementation phases. It was particularly helpful in:
- Designing the decoupled background processing pipeline for image ingestion.
- Writing the Pydantic schema validation to reliably parse the LLM structured output.
- Formulating the math for the Cosine Similarity ranking and Mismatch Guard logic in Python.
- Setting up the FastAPI routing and SQLite database architecture.

## Where AI Was Wrong
- Initially, the AI attempted to write an image download script using `urllib` to pull seed images from Unsplash. However, due to networking restrictions in my local environment, it failed with a `getaddrinfo` error. 
- The AI initially forgot to generate the `capstone.yaml` file required by the grading rubric.

## What I Changed
- I rejected the AI's idea of building a fake "mock" vision service and mandated that we use the real Gemini API for image parsing to ensure the project was authentic.
- Instead of using the failed download script, I manually generated the seed images (fox, dog, wolf, bear) using the AI's built-in image generator tool and placed them in the `images/` directory to act as my test corpus.
