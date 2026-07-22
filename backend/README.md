# DevSkillMapper Backend

FastAPI web backend for analyzing GitHub repository health.

## Local Development

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GITHUB_TOKEN | No | - | GitHub PAT for higher API rate limits |
| CORS_ORIGINS | No | localhost:5173,... | Allowed CORS origins |

## API Endpoints

- `GET /api/health` — Health check
- `POST /api/analyze` — Analyze a repository (body: `{"repo_full_name": "owner/repo"}`)

## Deployment

Deploy on Railway using `railway.json` or Dockerfile.
Set `CORS_ORIGINS` to your frontend URL.
Set `GITHUB_TOKEN` for production (avoids rate limiting).
