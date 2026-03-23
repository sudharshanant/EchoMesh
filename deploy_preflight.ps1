$ErrorActionPreference = "Stop"

Write-Host "[1/4] Validating Python syntax..."
& .\.venv\Scripts\python.exe -m py_compile .\echomesh_app.py

Write-Host "[2/4] Installing dependencies..."
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt

Write-Host "[3/4] Running quick import check..."
& .\.venv\Scripts\python.exe -c "import streamlit,pandas,numpy,pydeck; print('Imports OK')"

Write-Host "[4/4] Preflight complete."
Write-Host "Deployment config files are ready: render.yaml, railway.json, Dockerfile, Procfile"
