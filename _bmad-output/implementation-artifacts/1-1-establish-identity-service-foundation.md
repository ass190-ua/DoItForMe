# Story 1.1: Establish Identity Service Foundation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a new platform user,
I want the identity service foundation to be available,
so that registration and login can be delivered on a stable backend base.

## Acceptance Criteria

1. Given Epic 1 begins with identity capabilities, when the first story is implemented, then the backend provides the minimum service foundation required to support registration and login, and that foundation follows the agreed FastAPI architecture and project structure.
2. Given identity features require configuration and persistence support, when the foundation is established, then environment-based configuration, database session management, and migration support are available, and only the minimum infrastructure needed for identity features is introduced.
3. Given future identity endpoints must behave consistently, when the shared application layer is prepared, then API versioning, standardized response/error handling, and base security utilities are available, and registration and login behavior remains deferred to subsequent stories.
4. Given the story should enable immediate follow-on user value, when Story 1.1 is completed, then Story 1.2 can implement user registration without restructuring the project, and Story 1.3 can implement login using the same shared foundation.

## Tasks / Subtasks

- [x] Initialize the FastAPI project scaffold with `uv` and lock the baseline dependency set (AC: 1, 2)
  - [x] Create the project root using the architecture-selected manual scaffold (`uv init --name doitforme-api`)
  - [x] Add runtime dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[bcrypt]`
  - [x] Add test dependencies: `pytest`, `pytest-asyncio`, `httpx`
  - [x] Commit to the architecture-selected backend-only project layout rooted at `doitforme-api/app/`
- [x] Establish the shared application skeleton and versioned API entrypoints (AC: 1, 3)
  - [x] Create `app/main.py` as the ASGI entrypoint
  - [x] Create `app/api/deps.py` and `app/api/v1/router.py`
  - [x] Wire `/api/v1` routing and create minimal router aggregation without implementing registration/login endpoints yet
  - [x] Add `/health` and `/ready` endpoints as part of the operational baseline
- [x] Implement environment-based configuration and shared core utilities (AC: 2, 3)
  - [x] Create `app/core/config.py` using `pydantic-settings` and environment variables
  - [x] Provide `.env` and `.env.example` with the minimum required settings for local development
  - [x] Create `app/core/response.py` and `app/core/exceptions.py` for the standardized API envelope and centralized exception mapping
  - [x] Create `app/core/logging.py` for structured logging primitives that avoid secrets and raw tokens
- [x] Implement persistence foundations for identity work (AC: 2)
  - [x] Create `app/db/base.py` and `app/db/session.py` for SQLAlchemy async base metadata, engine, and session lifecycle
  - [x] Initialize Alembic and configure it for the project database connection
  - [x] Create the initial user persistence shape needed by auth foundations (`app/models/user.py`) aligned with the `users` table contract
  - [x] Keep transaction ownership in the service layer and persistence access in repositories only
- [x] Implement base security utilities without delivering auth endpoints yet (AC: 3, 4)
  - [x] Create `app/core/security.py` for password hashing helpers and JWT encode/decode primitives
  - [x] Define shared auth-related dependencies/guards stubs needed for later protected routes
  - [x] Align JWT payload handling to include `sub`, `email`, `role`, `iat`, and `exp`
  - [x] Leave registration and login endpoint/service behavior for Stories 1.2 and 1.3
- [x] Establish the test and delivery baseline for follow-on stories (AC: 1, 4)
  - [x] Create `tests/conftest.py` plus initial test package structure mirroring app layers
  - [x] Add smoke coverage for app startup, health/readiness endpoints, and shared dependency wiring
  - [x] Add Docker/local runtime scaffolding (`Dockerfile`, `docker-compose.yml`) and CI placeholders consistent with the architecture baseline

## Dev Notes

- This repository is currently planning-only. There is no existing FastAPI application code to extend, so this story creates the first real backend scaffold while following the generated architecture exactly.
- Scope boundary: deliver only the minimum shared platform foundation for auth-related stories. Do not implement `/auth/register`, `/auth/login`, or `/auth/logout` business behavior in this story.
- The architecture explicitly states that project initialization using `uv` is the first implementation priority, followed by config, database session management, Alembic, and auth/security foundations.
- The project is greenfield, backend-only, and should favor clarity and maintainability over premature complexity.

### Technical Requirements

- Backend stack must be Python + FastAPI with a manual `uv` scaffold.
- Database stack must be PostgreSQL + SQLAlchemy async + `asyncpg` + Alembic.
- Validation/config stack must use Pydantic v2 and `pydantic-settings`.
- Security stack must use `python-jose[cryptography]` for JWT and `passlib[bcrypt]` for password hashing per architecture.
- API must be rooted under `/api/v1` and expose FastAPI OpenAPI/Swagger docs.
- Responses must use the standardized success/error envelope across shared utilities before feature endpoints are added.
- Logging must be structured and must never include secrets, password hashes, or raw JWTs.
- Health and readiness endpoints are part of the required operational baseline.

### Architecture Compliance

- Follow the modular monolith boundaries: routers call services, services coordinate repositories, repositories handle persistence only.
- Keep routers thin and orchestration-focused.
- Keep transaction boundaries in the service layer; repositories must not own hidden commits.
- Use `snake_case` for Python modules, DB fields, and JSON fields.
- Keep application source under `app/` only.
- Put routers in `app/api/v1/`, shared dependencies in `app/api/deps.py`, core utilities in `app/core/`, DB session/base code in `app/db/`, models in `app/models/`, schemas in `app/schemas/`, services in `app/services/`, repositories in `app/repositories/`, and tests in `tests/`.
- Preserve the backend-only scope; no frontend or UX artifacts are required in implementation.

### Library / Framework Requirements

- FastAPI project structure should follow the “bigger applications” pattern with `APIRouter` modules and dependency injection.
- SQLAlchemy async setup should use `create_async_engine`, `async_sessionmaker`, and an async session dependency.
- Configure DB URLs with the `postgresql+asyncpg://` dialect.
- `expire_on_commit=False` is the recommended sessionmaker setting for async service flows.
- `pydantic-settings` should own environment-driven config loading from `.env` for local development.
- JWT utilities should use HS256, and token helpers should support the architecture payload fields (`sub`, `email`, `role`, `iat`, `exp`).
- Alembic should be initialized using the async template/pattern and wired to the project metadata.

### File Structure Requirements

- Expected root structure begins at `doitforme-api/`.
- Minimum Story 1.1 files/directories:
  - `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`
  - `.env`, `.env.example`, `Dockerfile`, `docker-compose.yml`, `alembic.ini`
  - `app/main.py`
  - `app/api/deps.py`, `app/api/v1/router.py`
  - `app/core/config.py`, `app/core/security.py`, `app/core/exceptions.py`, `app/core/response.py`, `app/core/logging.py`
  - `app/db/base.py`, `app/db/session.py`
  - `app/models/user.py`
  - `app/schemas/common.py`
  - `app/services/auth_service.py` and `app/repositories/user_repository.py` may be created as minimal placeholders only if needed to support the architecture skeleton, but endpoint logic belongs to later stories
  - `tests/conftest.py` and starter test folders
  - `alembic/env.py`, `alembic/versions/`

### Data / Persistence Notes

- The `users` table contract already exists in `_bmad-output/database-schema.md` and should drive the initial SQLAlchemy model shape:
  - `user_id` UUID primary key
  - `email` unique and required
  - `password_hash` required
  - `name` required
  - `role` constrained to `poster | performer | admin`
  - optional `latitude` / `longitude`
  - rating/stat counters and UTC timestamps
- Use UTC timestamp semantics.
- Follow DB naming conventions: plural table names, `snake_case` columns, `{entity}_id` foreign key pattern, and explicit indexes where schema requires them.

### API Contract Notes

- Standard success envelope:
  - `success: true`
  - `data: { ... }`
  - `error: null`
  - `timestamp: ISO-8601`
- Standard error envelope:
  - `success: false`
  - `data: null`
  - `error.code`, `error.message`, `error.details`
  - `timestamp: ISO-8601`
- Authentication contract already expects Bearer JWTs and token payload fields `sub`, `email`, `role`, `iat`, `exp`; shared utilities created here must make that possible later.
- The API contract document still shows mixed Flask/FastAPI wording and camelCase examples in payloads; implementation must follow the architecture’s final conventions: FastAPI, `/api/v1`, standardized envelope, and `snake_case` JSON field naming.

### Testing Requirements

- Use `pytest`, `pytest-asyncio`, and `httpx` as the testing baseline.
- Mirror application layers under `tests/api/`, `tests/services/`, and `tests/repositories/`.
- Story 1.1 should at minimum validate:
  - app startup succeeds
  - `/health` responds successfully
  - `/ready` responds successfully
  - shared configuration/session dependencies can be imported and wired without runtime errors
- Do not overbuild feature tests for registration/login yet; those belong to Stories 1.2 and 1.3.

### Deployment / Environment Requirements

- Local config uses `.env`; deployed environments use environment variables.
- Environment separation should support `local`, `test`, `staging`, and `production`.
- Development runtime is Uvicorn; production target is Gunicorn + Uvicorn workers.
- CI baseline should cover formatting/linting, tests, and migration validation.
- Dockerized deployment assumptions are required, even if only basic scaffolding is created now.

### Implementation Guardrails

- Do not skip straight to feature endpoints.
- Do not add WebSockets, Redis, background queues, or microservice decomposition in this story.
- Do not invent alternative folder structures or bypass service/repository boundaries.
- Do not duplicate auth logic in routers; create reusable shared utilities/dependencies instead.
- Do not return ad hoc JSON shapes from health or shared responses if they should use the standardized envelope.
- Do not add more than the minimum infrastructure needed to unblock registration and login follow-on stories.

### References

- Story 1.1 definition and acceptance criteria: [Source: _bmad-output/planning-artifacts/epics.md#Story-1.1]
- Architecture decisions, stack, structure, response envelope, and implementation sequence: [Source: _bmad-output/planning-artifacts/architecture.md]
- API response and auth contract: [Source: _bmad-output/api-contract.md]
- Users table schema and timestamp/role constraints: [Source: _bmad-output/database-schema.md]
- Product context and greenfield scope: [Source: _bmad-output/prd.md]
- External reference patterns: FastAPI bigger applications, FastAPI dependencies with yield, SQLAlchemy async ORM docs, FastAPI settings guide, and FastAPI OAuth2/JWT documentation.

## Project Structure Notes

- Current repo state: BMAD planning artifacts only; no implementation code exists yet.
- `docs/` exists but is empty and not a source of implementation constraints.
- Because there is no prior story implementation, there are no previous dev notes or git patterns to inherit.

## Dev Agent Record

### Debug Log

- 2026-03-19: Initialized `doitforme-api/` with `uv`, installed the story baseline runtime and test dependencies, and replaced the generated hello-world scaffold with the FastAPI application structure required by Story 1.1.
- 2026-03-19: Implemented environment-driven settings, standardized API envelopes and exception mapping, structured logging helpers, async SQLAlchemy base/session wiring, user persistence model, security helpers, shared auth dependency stubs, Alembic baseline, Docker scaffolding, and CI placeholder workflow.
- 2026-03-19: Validated the foundation with `uv run pytest` (5 passed) and `uv run alembic heads` (single migration head). Python LSP diagnostics were unavailable because `basedpyright-langserver` is not installed in this environment.

### Completion Notes

- Delivered the FastAPI backend foundation under `doitforme-api/` with `/api/v1`, `/health`, `/ready`, OpenAPI docs, centralized error handling, and standardized success/error response envelopes.
- Added PostgreSQL async session management, the initial `users` ORM model and Alembic migration, password hashing and JWT helpers, plus minimal repository/service/auth dependency placeholders that preserve the architecture boundaries without implementing registration or login behavior.
- Added smoke and wiring tests, Docker/local runtime scaffolding, and a CI placeholder so Stories 1.2 and 1.3 can implement registration and login without restructuring the backend.

## File List

- doitforme-api/.env
- doitforme-api/.env.example
- doitforme-api/.github/workflows/ci.yml
- doitforme-api/.gitignore
- doitforme-api/.python-version
- doitforme-api/Dockerfile
- doitforme-api/README.md
- doitforme-api/alembic.ini
- doitforme-api/alembic/env.py
- doitforme-api/alembic/script.py.mako
- doitforme-api/alembic/versions/0001_identity_foundation.py
- doitforme-api/app/__init__.py
- doitforme-api/app/api/__init__.py
- doitforme-api/app/api/deps.py
- doitforme-api/app/api/v1/__init__.py
- doitforme-api/app/api/v1/router.py
- doitforme-api/app/core/__init__.py
- doitforme-api/app/core/config.py
- doitforme-api/app/core/exceptions.py
- doitforme-api/app/core/logging.py
- doitforme-api/app/core/response.py
- doitforme-api/app/core/security.py
- doitforme-api/app/db/__init__.py
- doitforme-api/app/db/base.py
- doitforme-api/app/db/session.py
- doitforme-api/app/main.py
- doitforme-api/app/models/__init__.py
- doitforme-api/app/models/user.py
- doitforme-api/app/repositories/__init__.py
- doitforme-api/app/repositories/user_repository.py
- doitforme-api/app/schemas/__init__.py
- doitforme-api/app/schemas/common.py
- doitforme-api/app/services/__init__.py
- doitforme-api/app/services/auth_service.py
- doitforme-api/docker-compose.yml
- doitforme-api/pyproject.toml
- doitforme-api/tests/__init__.py
- doitforme-api/tests/api/__init__.py
- doitforme-api/tests/api/test_health.py
- doitforme-api/tests/conftest.py
- doitforme-api/tests/repositories/__init__.py
- doitforme-api/tests/repositories/test_wiring.py
- doitforme-api/tests/services/__init__.py
- doitforme-api/tests/services/test_auth_service.py
- doitforme-api/uv.lock

## Change Log

- 2026-03-19: Implemented Story 1.1 identity service foundation, including the project scaffold, shared FastAPI core, persistence/security baseline, Alembic migration, smoke tests, Docker scaffolding, and CI placeholder.
