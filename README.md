# ChatGum Control Panel starter

A FastAPI dashboard scaffold with 50 bot slots and 10 room slots.

## Important
- This is a control-panel scaffold, not a connected ChatGum client.
- Message sending is intentionally disabled until an official/authorized ChatGum API or documented integration is available.
- Do not upload ChatGum passwords, session cookies, tokens, or other secrets to this public repository.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.

## Deploy on Render
Create a **Web Service** from this GitHub repository and select **Docker** as the runtime. Render will use the included `Dockerfile`.

Health check path: `/health`
