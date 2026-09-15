# Project Management API

![CI](https://github.com/Hectorlu8/project-management-api/actions/workflows/ci.yml/badge.svg)

A REST API for managing users, projects, and tasks, built with FastAPI
and PostgreSQL. Users authenticate with JWT, own projects, and projects
contain tasks with a status and priority.

**Live demo:** https://project-management-api-313771756622.europe-west1.run.app/docs

## Features

- **CRUD** for users, projects, and tasks, backed by PostgreSQL via SQLAlchemy
- **Schema migrations** with Alembic
- **JWT authentication**: registration, login (`POST /token`), and protected
  endpoints via a `get_current_user` dependency
- **Filtering & pagination** on list endpoints (`status`/`priority`/`project_id`
  on tasks, `owner_id` on projects, `skip`/`limit` everywhere, capped at 100)
- **Consistent error handling**: a global handler converts database
  constraint violations into clean `409` responses
- **Request logging**: every request is logged with method, path, status
  code, and duration
- **Environment-based configuration** via `pydantic-settings`, with
  validation that fails fast on missing/invalid config
- **CI/CD**: every push runs the test suite and builds the Docker image;
  pushes to `main` also deploy automatically to Cloud Run

## Tech stack

Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · Pydantic ·
PyJWT · bcrypt · pytest · Docker · Docker Compose · GitHub Actions ·
Google Cloud Run

## Architecture

**Data model:** a `User` owns many `Project`s; a `Project` has many
`Task`s (`status`: To Do / In Progress / Done; `priority`: Low / Medium
/ High). Both relationships cascade-protect on delete — you can't
delete a user with projects, or a project with tasks, without removing
the dependents first.

**Request flow:** `main.py` routes → Pydantic schemas validate the
request body → the route handler queries/mutates via a SQLAlchemy
`Session` (injected per-request through `Depends(get_db)`) → the ORM
model is serialized back through a Pydantic response schema. Schemas
(`schemas.py`) and ORM models (`models.py`) are deliberately separate:
the former is the API's public contract, the latter is the database
table — mixing them was an early mistake in this project's history
that's now a hard rule in `CLAUDE.md`.

**Auth:** `POST /token` (OAuth2 password flow) verifies credentials and
issues a JWT. Protected endpoints depend on `get_current_user`, which
decodes the token, re-fetches the user from the database, and rejects
the request with `401` if the token is invalid, expired, or the user
no longer exists.

**Errors:** expected conflicts (e.g. duplicate email) raise a specific
`HTTPException`; unexpected database constraint violations are caught
by a global `IntegrityError` handler as a `409` safety net, so no raw
SQL error ever reaches a client.

**CI/CD:** every push runs `pytest` against a Postgres service
container and builds the Docker image; pushes to `main` additionally
push that image to Artifact Registry, run `alembic upgrade head`
against production as a one-off step, and deploy the new revision to
Cloud Run. See `.github/workflows/ci.yml`.

## Project structure

```
app/
  main.py       # FastAPI app, routes, middleware, exception handlers
  models.py     # SQLAlchemy ORM models (User, Project, Task)
  schemas.py    # Pydantic request/response schemas
  database.py   # Engine, session factory, declarative Base
  config.py     # Settings (pydantic-settings), loaded from .env
  security.py   # Password hashing and JWT creation/decoding
alembic/        # Database migrations
tests/          # pytest suite (unit + integration tests)
```

## Run with Docker (fastest way to try it)

```
cp .env.docker.example .env.docker
```

Fill in `.env.docker` (a `SECRET_KEY` and Postgres credentials — see
the file for the exact format), then:

```
docker compose up --build
```

This builds the API image, starts PostgreSQL in its own container, waits
for it to be healthy, applies migrations, and starts the API. It's
available at `http://localhost:8000/docs`. Data persists in a Docker
volume across restarts; run `docker compose down -v` to wipe it.

## Setup (without Docker)

### Prerequisites

- Python 3.11+
- A running PostgreSQL instance

### 1. Install dependencies

```
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure environment variables

```
cp .env.example .env
```

Fill in `DATABASE_URL` with your local PostgreSQL connection string, and
generate a `SECRET_KEY`:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Create the database and apply migrations

Create an empty PostgreSQL database matching your `DATABASE_URL` (e.g.
`project_management`), then run:

```
alembic upgrade head
```

### 4. Run the API

```
fastapi dev .\app\main.py
```

or equivalently:

```
uvicorn app.main:app --reload
```

Interactive API docs are available at `http://127.0.0.1:8000/docs`.

## Running tests

Tests run against a **separate** PostgreSQL database — never against your
development data. Its tables are dropped and recreated on every test run.

```
cp .env.test.example .env.test
```

Fill in `TEST_DATABASE_URL` pointing at a dedicated database (e.g.
`project_management_test`), create that empty database, then run:

```
pytest
```

## Status

`v1.0.0` — feature-complete for its scope as Project #1 of a backend
learning roadmap (Python/FastAPI focus): FastAPI CRUD, PostgreSQL +
Alembic migrations, JWT auth, filters/pagination, consistent error
handling, request logging, a pytest suite (unit, integration, and
mocking), a Docker/Compose setup, and a CI/CD pipeline that tests,
builds, and deploys to Cloud Run on every push to `main`. Authorization
is currently authentication-only (any logged-in user can act on any
resource) — ownership-based authorization is a known next step, not
yet implemented.

## License

[MIT](LICENSE)
