# Deploy To DigitalOcean

This project is set up to deploy as:

- a FastAPI backend service from `backend/`
- a static Vue frontend from `frontend/`

## 1. Push the repo to GitHub

DigitalOcean App Platform deploys from a Git provider or container registry.

## 2. Prepare production secrets and URLs

You need:

- `RIOT_API_KEY`
- your backend public URL
- your frontend public URL

The frontend needs the backend URL at build time via `VITE_API_BASE_URL`.
The backend needs the frontend URL at run time via `CORS_ORIGINS`.

## 3. Deploy the backend first

In DigitalOcean:

1. Create a new App Platform app.
2. Choose your GitHub repo.
3. Select `backend/` as the source directory for the service.
4. Use the Dockerfile at `backend/Dockerfile`.
5. Set the HTTP port to `8000`.
6. Add environment variables:
   - `RIOT_API_KEY` as a secret
   - `CORS_ORIGINS` temporarily as `https://placeholder.example`
7. Deploy.

After deploy, copy the backend URL.

## 4. Deploy the frontend

Create a second component or a second app for the frontend:

1. Select the same repo.
2. Use `frontend/` as the source directory.
3. Build command: `npm ci && npm run build`
4. Output directory: `dist`
5. Add build-time env:
   - `VITE_API_BASE_URL` = your backend public URL
6. Deploy.

After deploy, copy the frontend URL.

## 5. Fix backend CORS

Go back to the backend app and set:

- `CORS_ORIGINS` = your frontend public URL

Then redeploy the backend.

## 6. Optional: use the app spec template

There is a starter spec at `.do/app.yaml`.

Before using it, replace:

- `YOUR_GITHUB_USERNAME/YOUR_REPO_NAME`
- `REPLACE_WITH_RIOT_API_KEY`
- `https://replace-me-with-frontend-url.ondigitalocean.app`
- `https://replace-me-with-api-url.ondigitalocean.app`

## 7. Health check

The backend exposes:

- `/healthz`

Use that for App Platform health checks.
