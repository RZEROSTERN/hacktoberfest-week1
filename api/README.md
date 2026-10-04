# API

FastAPI backend for the project, consumed by the frontend in `../web`.

## Setup

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Development Server

```bash
fastapi dev app/main.py
```

The API runs on `http://localhost:8000`. Interactive docs are available at
`http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

## Production

```bash
fastapi run app/main.py
```
