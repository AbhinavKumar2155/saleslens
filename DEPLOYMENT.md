# SalesLens deployment: Vercel + Render

This project no longer requires Streamlit for the production interface.

## 1. Deploy the analytics API on Render

1. Push this repository to GitHub.
2. In Render, create a new **Blueprint** from the repository, or create a Web Service manually.
3. Use `api` as the root directory, `pip install -r requirements.txt` as the build command, and `gunicorn app:app` as the start command.
4. Wait for the health endpoint to respond at `/health`.

## 2. Deploy the frontend on Vercel

1. Import the same GitHub repository into Vercel.
2. Leave the Vercel root directory at the repository root. The root `vercel.json` builds `web/` and prevents the analytics Python environment from being detected as a Vercel function.
3. Add `VITE_API_URL` in Vercel Environment Variables with the Render service URL, for example `https://your-service.onrender.com`.
4. Deploy. Vercel builds the Vite application and handles single-page app navigation.

## Local development

Run the API from `api`:

```powershell
python -m pip install -r requirements.txt
flask --app app run --port 5000
```

Run the frontend from `web`:

```powershell
pnpm install
pnpm dev
```

For local frontend development, leave `VITE_API_URL` unset: Vite proxies API requests to `http://127.0.0.1:5000`.
