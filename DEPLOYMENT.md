# EdgeInfer Deployment Guide

## Running Locally

See **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** for step-by-step instructions using Docker, a local web app, or the CLI, plus troubleshooting.

The short version, with `.env` filled in:

```bash
docker compose up -d --build
```

The UI is served on `http://localhost:3000` and the API on `http://localhost:5000`.

## Before Deploying Publicly

EdgeInfer is ready to run locally, but a public deployment needs a few changes first:

- **Production server:** the backend currently runs on Flask's development server. Use a WSGI server such as Gunicorn, with a request timeout of at least 300 seconds for long code generation.
- **Authentication and rate limiting:** the API has neither, so anyone who can reach it can spend your LLM credits.
- **CORS:** the API currently accepts requests from any origin. Restrict it to your frontend's domain.

## Production Options

Both services are standard containers, so any container platform works (for example Google Cloud Run, AWS App Runner or ECS, Azure Container Apps, Render or Fly.io).

### Backend

- Build the image from the root `Dockerfile`.
- Expose port 5000.
- Provide the settings from `.env.example` as environment variables or secrets on the platform, never inside the image.

### Frontend

Either run the `client/Dockerfile` image alongside the backend, or build static files and host them on Vercel, Netlify or any static host:

```bash
cd client
npm install
VITE_API_URL=https://api.yourdomain.com/api npm run build   # output in client/dist/
```

`VITE_API_URL` is applied at build time, so rebuild the frontend if the API address changes.

## Environment Variables

### Backend (`.env`)

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | `anthropic` or `ollama` |
| `ANTHROPIC_API_KEY`, `MODEL`, `EFFORT` | Claude settings |
| `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_API_KEY` | Ollama settings |

### Frontend

| Variable | Description |
|---|---|
| `VITE_API_URL` | API address when the UI and API are on different domains (build time) |
| `API_PROXY_TARGET` | Where the Vite dev/preview server forwards `/api` (default `http://localhost:5000`) |

## CI/CD

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

- backend tests on Python 3.10 and 3.13;
- frontend type-check and production build.

There is no automatic deployment step yet.
