# EdgeInfer Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- An Anthropic API key, or an Ollama install / Ollama Cloud key

To use Ollama instead of Claude, set `LLM_PROVIDER=ollama` in `.env` along with `OLLAMA_BASE_URL`, `OLLAMA_MODEL` and (for Ollama Cloud) `OLLAMA_API_KEY`.
- npm or yarn

### Start Backend

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then set ANTHROPIC_API_KEY or the Ollama settings
python server.py
```

Backend runs on `http://localhost:5000`

### Start Frontend

```bash
cd client
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` and proxies `/api` to the backend

### Docker Compose

```bash
cp .env.example .env  # then set ANTHROPIC_API_KEY
docker compose up --build
```

The UI is served on `http://localhost:3000` and the API on `http://localhost:5000`.

## Production Deployment

### Vercel (Frontend)

```bash
cd client
npm install -g vercel
vercel deploy --prod
```

### Heroku (Backend)

```bash
# Create Heroku app
heroku create edgeinfer-api

# Deploy
git push heroku main
```

### AWS (Full Stack)

1. **Frontend**: S3 + CloudFront
2. **Backend**: Lambda + API Gateway
3. **Database**: DynamoDB (optional)

### Google Cloud

1. **Frontend**: Cloud Storage + Cloud CDN
2. **Backend**: Cloud Run
3. **Database**: Firestore (optional)

## Environment Variables

### Backend (.env)
```
ANTHROPIC_API_KEY=your_key_here
FLASK_ENV=production
```

### Frontend (.env.local)
```
REACT_APP_API_URL=https://api.yourdomain.com
```

## Monitoring

- Frontend errors: Sentry or Rollbar
- Backend logs: CloudWatch or Stackdriver
- Performance: New Relic or Datadog

## CI/CD

### GitHub Actions

See `.github/workflows/` for:
- Frontend tests and build
- Backend tests
- Deployment on push to main

