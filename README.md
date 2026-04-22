# Module 12 — User & Calculation API with FastAPI and CI/CD

**Author:** Kamalesh — ks2435@njit.edu
**Repo:** https://github.com/ks2435/module12_is601
**Docker Hub:** https://hub.docker.com/r/ks2435/fastapi-calculations

## Overview

FastAPI backend combining the User model (Module 10) and the Calculation model (Module 11):

- `POST /users/register` — register with bcrypt-hashed password.
- `POST /users/login` — verify password, return the user record.
- `GET /calculations` — Browse.
- `GET /calculations/{id}` — Read.
- `POST /calculations` — Add (computes result via factory; requires `user_id`).
- `PUT /calculations/{id}` — Edit (recomputes result).
- `DELETE /calculations/{id}` — Delete.

## Run Locally

```
docker compose up --build
```

Then open http://localhost:8000/docs.

Or run the app directly against the bundled Postgres:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d db
uvicorn main:app --reload
```

## Manual Check via OpenAPI

1. Visit `/docs`.
2. `POST /users/register` with `{"username":"alice","email":"alice@example.com","password":"pw"}`.
3. `POST /users/login` with `{"username":"alice","password":"pw"}` — note the returned `id`.
4. `POST /calculations` with `{"a":10,"b":4,"type":"add","user_id":<id>}`.
5. Exercise GET / PUT / DELETE on `/calculations/{id}`.

## Run Tests Locally

Integration tests require a running Postgres:

```
docker compose up -d db
python -m pytest tests -v
```

## CI/CD

`.github/workflows/ci.yml` spins up Postgres, runs all tests, and on a successful `master` push builds and pushes the Docker image to Docker Hub.

Required repo secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.

## Pull the Docker Image

```
docker pull ks2435/fastapi-calculations:latest
```

## Reflection

**What I built.** I merged the User model from Module 10 and the Calculation model from Module 11 behind one FastAPI app. Passwords are hashed with bcrypt; the `/users/login` endpoint verifies them and returns the user record. Calculation endpoints implement full BREAD, with each calculation linked to a `user_id`.

**Key decisions.** I kept the code in a small number of files on purpose — one `main.py` with all routes, one `models.py` with both tables, one `schemas.py` with all Pydantic models. Splitting them would have been fine for a larger project but added ceremony without clarity here. Divide-by-zero is enforced in two places: the Pydantic validator on `CalculationCreate` (returns 422 on create) and the factory's `ValueError` (returns 400 on PUT with `b=0`). Two layers because a field validator only fires on the create schema.

**Challenges.** The Module 10 `main.py` was missing `from fastapi import FastAPI` and `app = FastAPI()` — the file started at the first `@app.post` decorator, so imports would have failed. I rewrote it cleanly. Clean test isolation needed care: each test runs against `TRUNCATE ... RESTART IDENTITY CASCADE` so IDs are predictable and the FK from calculations to users is honored. For CI, the Postgres service container needed a health check plus a short `pg_isready` loop so the first test run didn't race the database.

**What I'd add next.** JWT tokens for real session auth (the assignment flagged it as optional), pagination on `GET /calculations`, and ownership checks so users only see their own calculations.
