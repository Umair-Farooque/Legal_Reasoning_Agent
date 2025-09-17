# Legal Reasoning Agent (RAG) Project
---
**Legal Reasoning Agent** is an AI-powered system that provides structured, professional legal answers based on the **Pakistan Constitution**. It combines **BM25 keyword search**, **dense embeddings with FAISS**, and **OpenAI GPT-4o-mini** for reasoning and context-aware responses.

## Features

- FastAPI web app for query submission.
- Dense vector retrieval using FAISS.
- Keyword-based retrieval using BM25.
- Integration with OpenAI GPT for generating professional legal responses.
- Templates and static files for a user-friendly web interface.

---

## Project Structure

```
app/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── constitution.index     # FAISS index file
├── embeddings.npy         # Precomputed embeddings
├── constitution_metadata.csv # Metadata of constitutional sections
├── templates/             # HTML templates
└── static/                # CSS, JS, and other static assets
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Umair-Farooque/Legal_Reasoning_Agent.git
```

### 2. Set environment variables

Render automatically sets environment variables, including `PORT`. You also need:

- `OPENAI_API_KEY` — your OpenAI API key.

Example for local development (optional):

```bash
export OPENAI_API_KEY='your_openai_api_key'
export PORT=8000
```

### 3. Install dependencies (local testing)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run locally (optional)

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

## Deployment (Render)

1. Push your repository to GitHub.
2. Connect your repository in Render as a Web Service.
3. Use the following Dockerfile for production deployment:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
```

4. Set the environment variable `OPENAI_API_KEY` in Render.
5. Deploy and Render will automatically use the `PORT` variable for web binding.

---

## Usage

- Navigate to the deployed web app.
- Enter your constitutional query.
- The agent retrieves relevant sections and generates a professional legal answer.

---

## Notes

- Only queries related to the provided constitutional text are supported.
- The model strictly uses retrieved sections to formulate responses.
- FAISS and BM25 retrieval ensure both semantic and keyword-based search.

---

## References

- [FAISS](https://github.com/facebookresearch/faiss)
- [BM25Okapi](https://github.com/dorianbrown/rank_bm25)
- [OpenAI API](https://platform.openai.com/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Render Deployment Docs](https://render.com/docs/web-services)

---

## License

MIT License

