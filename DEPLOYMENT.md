# EdgeInfer Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Start Backend

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install flask flask-cors
python server.py
```

Backend runs on `http://localhost:5000`

### Start Frontend

```bash
cd client
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### Docker Compose

```bash
docker-compose up
```

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

