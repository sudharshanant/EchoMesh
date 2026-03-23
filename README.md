# EchoMesh

EchoMesh is a Streamlit-based emergency coordination prototype with:
- Public SOS submission
- Rescue team dashboard
- Local JSON persistence fallback
- Optional Firebase Realtime Database support

## Quick Start (Local)

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run echomesh_app.py --server.headless true --server.port 8502
```

4. Open:

```text
http://localhost:8502
```

## Firebase (Optional)

To enable Firebase storage:
- Add your Firebase service account key file (default path: `serviceAccountKey.json`).
- Set `FIREBASE_DATABASE_URL` in your environment.

If Firebase is not configured, the app automatically uses `local_requests.json`.

## Environment Variables

- `PORT`: runtime port (default: `8502`)
- `ECHO_DATA_FILE`: local JSON fallback data file path (default: `local_requests.json`)
- `FIREBASE_KEY_PATH`: Firebase service account key path (default: `serviceAccountKey.json`)
- `FIREBASE_DATABASE_URL`: Firebase Realtime Database URL (required for Firebase mode)

See `.env.example` for a ready-to-copy template.

## Deployment

Use this start command in your hosting platform:

```bash
streamlit run echomesh_app.py --server.headless true --server.address 0.0.0.0 --server.port $PORT
```

For platforms that do not provide `$PORT`, replace with a fixed port (for example `8502`).

The repository also includes:
- `Procfile` for process-based hosts
- `.streamlit/config.toml` for production-friendly Streamlit defaults

## Zero-Touch Deploy Runbook

Run this once before shipping:

```powershell
.\deploy_preflight.ps1
```

Health endpoint after deployment:

```text
https://YOUR_APP_URL/_stcore/health
```

### Render

This repo already includes `render.yaml`.

1. Push this project to a Git provider.
2. In Render, create a new Blueprint deploy from that repository.
3. Set secret values in Render:
	- `FIREBASE_DATABASE_URL` (if using Firebase)
	- Upload `serviceAccountKey.json` as a secret file (path should match `FIREBASE_KEY_PATH`)
4. Deploy.

### Railway

This repo already includes `railway.json`.

1. Create a new Railway project from this repository.
2. Add environment variables:
	- `PORT` (Railway typically injects this automatically)
	- `FIREBASE_DATABASE_URL` (optional)
	- `FIREBASE_KEY_PATH` (optional, if using Firebase key file)
3. Deploy.

### Docker (Any VM or Container Platform)

Build image:

```bash
docker build -t echomesh:latest .
```

Run container:

```bash
docker run --rm -p 8502:8502 --env PORT=8502 echomesh:latest
```

With Firebase enabled:

```bash
docker run --rm -p 8502:8502 \
  --env PORT=8502 \
  --env FIREBASE_DATABASE_URL=https://YOUR_PROJECT.firebaseio.com/ \
  --env FIREBASE_KEY_PATH=/run/secrets/serviceAccountKey.json \
  -v /path/to/serviceAccountKey.json:/run/secrets/serviceAccountKey.json:ro \
  echomesh:latest
```

## Project Files

- `echomesh_app.py`: main Streamlit app
- `echomesh_system.py`: alternate simulation workflow
- `local_requests.json`: local fallback request storage
- `data/logs.txt`: log file
