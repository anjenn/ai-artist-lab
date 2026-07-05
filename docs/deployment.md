# Deployment Notes

This project is still a portfolio/demo app. Before public deployment, configure:

- `APP_ENV=production`
- `DATABASE_URL` for a persistent database
- `OPENAI_API_KEY` only if real model calls are desired
- `DEMO_ACCESS_KEY` to enable the lightweight demo access gate
- `EMBEDDING_PROVIDER=hash` for deterministic demo retrieval or `openai` for API-backed embeddings

Local container smoke test:

```bash
docker build -t blue-garage-ai-artist-lab .
docker run --rm -p 8000:8000 --env APP_ENV=production blue-garage-ai-artist-lab
```

Database migration flow:

```bash
cd backend
alembic upgrade head
python -m app.db.seed
```

`deploy/render.yaml` is a starter web-service spec. Keep secrets in the hosting provider's secret store, not in this repository.
