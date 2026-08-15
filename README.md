# DecisionOS V2 Backend

Backend API for DecisionOS V2.

This README is the **local backend setup guide for frontend and backend
developers**. It is based on the current repository configuration.

## Stack

-   Python **3.13.x** (`>=3.13,<3.14`)
-   FastAPI
-   Uvicorn
-   SQLAlchemy 2.x
-   PostgreSQL
-   Alembic
-   Pydantic Settings
-   JWT authentication
-   Qdrant / sentence-transformers for Knowledge infrastructure
-   TaskIQ / Redis infrastructure
-   `uv` for dependency and project management

Dependencies are defined in `pyproject.toml` and locked in `uv.lock`.

------------------------------------------------------------------------

## 1. Clone the Backend

``` bash
git clone <BACKEND_REPOSITORY_URL>
cd DecisionOS_v2
```

The normal integration branch is `develop`.

``` bash
git checkout develop
git pull origin develop
```

Create a feature branch for your work:

``` bash
git checkout -b feature/<feature-name>
```

Do not commit directly to `main`.

------------------------------------------------------------------------

## 2. Prerequisites

Install:

-   Git
-   Python 3.13.x
-   `uv`
-   PostgreSQL

The current repository also contains `Dockerfile` and
`docker-compose.yml`, but they are currently empty. **Do not use Docker
as the local setup path for this backend at the current checkpoint.**

PostgreSQL therefore needs to be available locally.

------------------------------------------------------------------------

## 3. Install `uv`

If `uv` is not already installed, install it using the official `uv`
installation method for your operating system.

Verify:

``` bash
uv --version
```

Verify Python:

``` bash
python --version
```

It must be Python 3.13.x.

------------------------------------------------------------------------

## 4. Install Project Dependencies

From the repository root:

``` bash
uv sync
```

This uses the committed `pyproject.toml` and `uv.lock`.

For development dependencies, `uv sync` installs the project's
development dependency group as configured by the project.

Do **not** create or use a `requirements.txt` file. This project uses
`uv`.

------------------------------------------------------------------------

## 5. Configure Environment

The backend loads configuration from a local `.env` file.

Copy `.env.example` to `.env`:

### Windows PowerShell

``` powershell
Copy-Item .env.example .env
```

### macOS / Linux

``` bash
cp .env.example .env
```

The current `.env.example` contains:

``` env
# ===== Application =====================================================
APP_NAME=DecisionOS
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
API_VERSION=0.1.0

# ===== Database ========================================================
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=decisionosv2
DATABASE_USER=postgres
DATABASE_PASSWORD=change-me
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=1800

# ===== Security ========================================================
JWT_SECRET_KEY=replace-with-a-64-character-random-hex-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ===== Web =============================================================
CORS_ORIGINS=["http://localhost:5173"]
TRUSTED_HOSTS=["localhost", "127.0.0.1", "testserver"]

# ===== Rate limiting ===================================================
RATE_LIMIT_ENABLED=false
RATE_LIMIT=100/minute
```

Change at least:

``` text
DATABASE_PASSWORD
JWT_SECRET_KEY
```

to values appropriate for your local environment.

Generate a development JWT secret with:

``` bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit `.env`.

------------------------------------------------------------------------

## 6. PostgreSQL Setup

The current development configuration expects PostgreSQL at:

``` text
host: localhost
port: 5432
database: decisionosv2
user: postgres
```

Create the database if it does not already exist:

``` sql
CREATE DATABASE decisionosv2;
```

Then make sure the values in `.env` match your local PostgreSQL
installation.

The application constructs its async connection from:

``` text
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
```

Alembic uses the same settings to construct its synchronous `psycopg`
connection.

You do **not** put a database URL into `alembic.ini`.

------------------------------------------------------------------------

## 7. Run Migrations

Alembic migrations are located at:

``` text
src/decisionos/core/database/migrations/
```

Run the current migration head:

``` bash
uv run alembic upgrade head
```

Check migration state:

``` bash
uv run alembic current
```

View migration history:

``` bash
uv run alembic history
```

Current repository migrations include:

``` text
0001_identity_users.py
0002_add_workspaces_and_decisions.py
0003_knowledge_documents.py
```

Do not manually create tables that are managed by migrations.

------------------------------------------------------------------------

## 8. Start the Backend

The FastAPI application is:

``` text
decisionos.main:app
```

Start the development server with:

``` bash
uv run uvicorn decisionos.main:app --reload
```

The backend runs at:

``` text
http://localhost:8000
```

------------------------------------------------------------------------

## 9. Verify the Backend

Open:

``` text
http://localhost:8000/docs
```

FastAPI Swagger UI is the primary way to inspect the currently
registered API contract.

OpenAPI JSON is available at:

``` text
http://localhost:8000/openapi.json
```

The running application is the source of truth for which endpoints are
currently exposed.

Do not assume an endpoint exists because it is mentioned in the roadmap
or frontend specification.

------------------------------------------------------------------------

## 10. Frontend Connection

The frontend development server is expected to run on:

``` text
http://localhost:5173
```

The backend's default CORS configuration already allows:

``` text
http://localhost:5173
```

Therefore the normal local setup is:

``` text
Frontend
http://localhost:5173
        │
        │ HTTP API
        ▼
Backend
http://localhost:8000
        │
        ▼
PostgreSQL
localhost:5432
```

The frontend should use a configurable API base URL rather than
hardcoding backend URLs throughout the application.

------------------------------------------------------------------------

## 11. Authentication

Identity is implemented and uses JWT authentication.

The current Identity API includes:

``` text
POST /identity/register
POST /identity/login
GET  /identity/me
```

The frontend should:

1.  Register or log in through the backend.
2.  Maintain the returned authentication state according to the agreed
    frontend implementation.
3.  Attach authentication credentials to protected API requests.
4.  Handle `401 Unauthorized` centrally.
5.  Redirect unauthenticated users to the login flow.

The backend is authoritative for authentication and authorization.

The frontend must not treat client-side checks as security enforcement.

Password hashes are never returned as frontend data.

------------------------------------------------------------------------

## 12. Current Backend Structure

The repository uses a modular, layered backend architecture.

``` text
src/
└── decisionos/
    ├── api/
    ├── core/
    │   ├── config/
    │   ├── database/
    │   ├── exceptions/
    │   ├── health/
    │   ├── logging/
    │   ├── middleware/
    │   ├── security/
    │   └── taskiq/
    │
    └── modules/
        ├── context/
        ├── decisions/
        ├── identity/
        ├── knowledge/
        ├── rag/
        └── workspaces/
```

The intended dependency direction is:

``` text
Router / API
      ↓
Service / Application
      ↓
Domain
      ↓
Repository / Infrastructure
      ↓
Database
```

Domain modules own their models, schemas, repositories, services,
routers, and relevant tests.

------------------------------------------------------------------------

## 13. Current Backend Modules

### Identity

Completed authentication/user foundation.

Includes:

-   user persistence
-   registration
-   login
-   password hashing/verification
-   JWT authentication
-   protected-route support
-   authentication tests

### Workspace

Workspace module is present in the current working tree and is part of
the current Workspace + Decision implementation work.

### Decision

Decision module is present in the current working tree and is part of
the current Workspace + Decision implementation work.

### Knowledge

Knowledge infrastructure includes:

-   documents
-   chunks
-   chunking
-   embeddings
-   embedding provider
-   vector store
-   OCR infrastructure
-   document processing

### RAG

RAG services/schemas/router are present for retrieval-related
functionality.

### Context

Context services and prompt-related functionality are present.

Not every module listed above should be assumed to represent a finished
product feature. Use the running API and current feature ticket status
to determine implementation completeness.

------------------------------------------------------------------------

## 14. Development Commands

### Install/synchronize environment

``` bash
uv sync
```

### Start API

``` bash
uv run uvicorn decisionos.main:app --reload
```

### Run all tests

``` bash
uv run pytest
```

### Run a specific test module

``` bash
uv run pytest tests/modules/identity/test_api.py
```

Replace the path with the relevant test file.

### Lint

``` bash
uv run ruff check .
```

### Format

``` bash
uv run ruff format .
```

### Type checking

``` bash
uv run mypy src
```

------------------------------------------------------------------------

## 15. Useful Backend Checks

Check that the application imports and routes can be constructed:

``` bash
uv run python -c "from decisionos.main import app; print([r.path for r in app.routes])"
```

Check Git state:

``` bash
git status
```

Inspect changes before committing:

``` bash
git diff
```

------------------------------------------------------------------------

## 16. Troubleshooting

### `uv` command not found

Install `uv` and verify:

``` bash
uv --version
```

### Wrong Python version

The project requires:

``` text
>=3.13,<3.14
```

Check:

``` bash
python --version
uv python list
```

Use Python 3.13.x for this project.

### Database connection failure

Check:

-   PostgreSQL is running.
-   PostgreSQL is listening on `localhost:5432`.
-   Database `decisionosv2` exists.
-   `DATABASE_USER` is correct.
-   `DATABASE_PASSWORD` is correct.
-   `.env` is present in the repository root.

### Migration failure

Check:

``` bash
uv run alembic current
uv run alembic heads
uv run alembic history
```

Do not bypass migration history by manually modifying the schema.

### `401 Unauthorized`

Check:

-   login succeeded
-   authentication credentials are attached to the request
-   the token is valid/not expired
-   the endpoint is actually protected
-   the request is being sent to `http://localhost:8000`

Use Swagger to reproduce the request independently from the frontend.

### CORS error from the frontend

Confirm the frontend is running on:

``` text
http://localhost:5173
```

The default backend configuration allows that origin.

If the frontend uses another origin, update `CORS_ORIGINS` in `.env`.

------------------------------------------------------------------------

## 17. Backend + Frontend Development Rules

### Backend is authoritative

Backend owns:

-   authentication
-   authorization
-   business rules
-   validation that affects correctness
-   lifecycle transitions
-   persistence
-   API contracts

Frontend validation is for user experience and must not replace backend
enforcement.

### Do not invent API contracts

If the frontend needs an endpoint that does not currently exist:

1.  Check `/docs`.
2.  Check the relevant backend router/schema.
3.  Discuss the required contract with the backend developer.
4.  Implement the agreed contract on both sides.

Do not silently invent request or response shapes.

### Keep API types aligned

Frontend types should correspond to backend request/response schemas.

Avoid untyped `any` API handling.

### Do not hardcode backend data

The frontend should consume the API.

Temporary mock data is acceptable only when an endpoint is not
implemented yet, and it should be isolated so it can be replaced
cleanly.

------------------------------------------------------------------------

## 18. Project Documentation

Important project documentation is under:

``` text
docs/
├── 01-system-architecture.md
├── 02-Domain-model.md
├── 03-application-architecture.md
├── 04-infrastructure-architecture.md
├── 05_Feature_Ticket_List.md
└── 06_Frontend_Specification.md
```

Use these documents for architecture, domain behavior, implementation
order, and frontend requirements.

The current execution pointer is:

``` text
[x] Foundation
[x] Identity

→ Workspace
→ Decision
```

Do not jump to later AI capabilities before the core decision domain is
stable.

------------------------------------------------------------------------

## 19. Git Workflow

Normal integration flow:

``` text
main
  ↑
develop
  ↑
feature/<feature-name>
```

Work on a feature branch.

``` bash
git checkout develop
git pull origin develop
git checkout -b feature/<feature-name>
```

Before opening a PR:

``` bash
uv run ruff check .
uv run pytest
git status
git diff
```

PRs should target `develop`, not `main`.

------------------------------------------------------------------------

## 20. Minimal Local Setup

If you already have Python 3.13, `uv`, and PostgreSQL installed:

``` bash
git clone <BACKEND_REPOSITORY_URL>
cd DecisionOS_v2

uv sync

# Create .env from .env.example and configure PostgreSQL/JWT values.

uv run alembic upgrade head

uv run uvicorn decisionos.main:app --reload
```

Then open:

``` text
http://localhost:8000/docs
```

That's the complete backend startup path for the current local
development setup.
