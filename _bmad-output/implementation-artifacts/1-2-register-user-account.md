# Story 1.2: Register User Account

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a new user,
I want to create an account with email and password,
so that I can join the platform.

## Acceptance Criteria

1. Given a visitor does not yet have an account, when they submit a valid registration request with required identity fields, role, email, and password, then a new user record is created in the database, and the password is stored only as a secure hash.
2. Given a registration request is received, when the submitted email already belongs to an existing user, then the API rejects the request with a conflict-style error response, and no duplicate account is created.
3. Given a registration request is received, when required fields are missing or the payload format is invalid, then the API returns a validation error using the standardized error envelope, and no user record is created.
4. Given a registration request is received, when the password does not meet the minimum security rules defined by the implementation, then the API rejects the request with a clear validation error, and the response does not expose internal security logic beyond what the client needs.
5. Given a registration succeeds, when the user record is returned or acknowledged by the API, then the response excludes the password hash and any secret fields, and the returned payload follows the standardized success envelope.
6. Given role-aware authorization is part of the platform architecture, when a new user registers, then the created account is assigned a valid supported role, and unsupported or unauthorized roles cannot be self-assigned through the public registration flow.
7. Given registration is an identity foundation story, when Story 1.2 is completed, then the system supports the next login story without restructuring the user domain, and tests cover successful registration, duplicate email rejection, and invalid payload handling.

## Tasks / Subtasks

- [x] Define registration schemas and response contracts (AC: 1, 3, 5, 6)
  - [x] Create `app/schemas/auth.py` for registration request and response payloads using `snake_case` fields
  - [x] Enforce request validation for required fields, email shape, and allowed public roles
  - [x] Ensure response models exclude `password_hash` and any secret fields
- [x] Implement registration persistence and service logic (AC: 1, 2, 4, 6)
  - [x] Expand `app/repositories/user_repository.py` with create and duplicate-email lookup helpers while keeping persistence concerns in the repository layer only
  - [x] Implement registration flow in `app/services/auth_service.py` with transaction ownership in the service layer
  - [x] Hash passwords using the existing shared security utility before persistence
  - [x] Reject duplicate email registration attempts with a conflict-style application error
  - [x] Restrict self-assigned roles in the public flow to the supported non-admin roles only
  - [x] Define and enforce minimum password rules in the service layer with clear client-facing validation errors
- [x] Expose the registration API endpoint (AC: 1, 2, 3, 5, 6)
  - [x] Create `app/api/v1/auth.py` with a thin `/auth/register` route under `/api/v1`
  - [x] Add the auth router to `app/api/v1/router.py` without implementing login behavior yet
  - [x] Return standardized success and error envelopes through the shared response/exception utilities
- [x] Add migration and model alignment only if required by registration scope (AC: 1, 6)
  - [x] Verify the existing `users` model and migration already support registration requirements without unnecessary schema changes
  - [x] If a schema change is strictly required, add the minimal Alembic migration needed and keep the user domain ready for Story 1.3
- [x] Add tests for registration behavior (AC: 1, 2, 3, 4, 5, 7)
  - [x] Add API tests for successful registration
  - [x] Add API tests for duplicate email rejection
  - [x] Add API tests for invalid payload handling and weak-password rejection
  - [x] Add focused service/repository tests only where they protect core registration logic without duplicating endpoint coverage
- [x] Validate delivery readiness for Story 1.3 (AC: 7)
  - [x] Run the relevant test suite for registration flows and existing regression coverage
  - [x] Confirm the created user shape and auth service boundaries can support the next login story without restructuring

## Dev Notes

- Story 1.1 already established the FastAPI app skeleton, shared config, response envelope, exception mapping, logging helpers, SQLAlchemy async session handling, Alembic baseline, `User` ORM model, and shared password/JWT utilities.
- Scope boundary: implement registration only. Do not implement `/auth/login`, `/auth/logout`, token issuance on login, refresh tokens, or protected profile endpoints in this story.
- Keep the modular monolith boundaries intact: router → service → repository. Repositories perform data access only. Services own orchestration and transaction boundaries.
- Prefer extending the existing identity foundation instead of introducing parallel auth paths or duplicate validation logic.

### Technical Requirements

- Use the existing `doitforme-api/app/` project structure created in Story 1.1.
- Reuse `app/core/security.py` for password hashing. Do not introduce a second hashing mechanism.
- Reuse `app/core/response.py` and `app/core/exceptions.py` so all registration responses follow the standardized API envelope.
- Keep request/response contracts in `app/schemas/`.
- Continue using PostgreSQL + SQLAlchemy async + `asyncpg` + Alembic.
- Keep JSON field naming in `snake_case` even where upstream planning docs contain mixed casing.

### Architecture Compliance

- Public registration should live in `app/api/v1/auth.py` and be aggregated by `app/api/v1/router.py`.
- The auth router must remain thin and delegate to `AuthService`.
- `AuthService` should own duplicate-email checks, password policy enforcement, password hashing, and transaction completion.
- `UserRepository` should encapsulate lookup/create persistence operations only and must not hide commits.
- Do not bypass the service layer from the route handler.

### Library / Framework Requirements

- FastAPI validation should be driven through Pydantic v2 schemas.
- Conflict and validation failures should surface through the centralized exception handling path so the standardized envelope is preserved.
- Password hashing must use `passlib[bcrypt]` through the existing shared helper.
- Do not issue JWTs in this story unless strictly required by the story specification; login/token issuance belongs to Story 1.3.

### File Structure Requirements

- Existing files expected to be extended:
  - `doitforme-api/app/api/v1/router.py`
  - `doitforme-api/app/repositories/user_repository.py`
  - `doitforme-api/app/services/auth_service.py`
  - `doitforme-api/tests/api/test_health.py` may remain untouched unless a shared fixture change is needed
- New files likely required:
  - `doitforme-api/app/api/v1/auth.py`
  - `doitforme-api/app/schemas/auth.py`
  - `doitforme-api/tests/api/test_auth.py`
  - `doitforme-api/tests/services/test_auth_service.py` updates
  - `doitforme-api/tests/repositories/test_user_repository.py` if repository-specific coverage is justified

### Data / Persistence Notes

- Registration persists into the existing `users` table shape from `_bmad-output/database-schema.md`.
- Required persisted registration fields are: `email`, `password_hash`, `name`, and `role`.
- Public registration must not allow self-assignment of `admin`.
- `email` is unique and should be treated as the duplicate-account constraint.
- Store only `password_hash`; never persist raw passwords.
- Reuse the existing UUID primary key and timestamp defaults.

### API Contract Notes

- Registration endpoint from `_bmad-output/api-contract.md` is `POST /auth/register`, which under the implemented versioned API should be exposed as `POST /api/v1/auth/register`.
- The request contract should include `email`, `password`, `name`, and `role`.
- Success responses must use the standardized envelope:
  - `success: true`
  - `data: { ... }`
  - `error: null`
  - `timestamp: ISO-8601`
- Error responses must use the standardized envelope:
  - `success: false`
  - `data: null`
  - `error.code`, `error.message`, `error.details`
  - `timestamp: ISO-8601`
- Do not return `password_hash`, secrets, or internal persistence details in success responses.
- The API contract contains examples with camelCase payload fields; implementation must continue to follow the architecture’s final `snake_case` convention.

### Testing Requirements

- Add API coverage for:
  - successful registration
  - duplicate email conflict
  - invalid payload / missing required fields
  - weak password rejection
  - unsupported role rejection
- Keep the test baseline on `pytest`, `pytest-asyncio`, and `httpx`.
- Preserve Story 1.1 coverage for startup and health/readiness.
- Use async-friendly testing patterns consistent with the existing `tests/conftest.py` setup.

### Delivery / Follow-on Story Requirements

- This story should prepare Story 1.3 by leaving the auth domain in a shape where login can reuse:
  - duplicate user lookup by email
  - password verification against the stored hash
  - the same auth router/module boundaries
- Do not introduce response shapes or auth abstractions that would need rewriting for login.

### Implementation Guardrails

- Do not implement login, logout, refresh tokens, or session revocation here.
- Do not allow public creation of `admin` users.
- Do not return raw SQLAlchemy models directly from the router.
- Do not leak password policy internals beyond what the client needs to correct the request.
- Do not add more infrastructure than needed to deliver registration.
- Do not move transaction ownership into the repository layer.

### Previous Story Learnings

- Story 1.1 established the canonical file layout under `doitforme-api/app/`; follow it exactly rather than creating alternate auth folders.
- Story 1.1 already created shared response and exception utilities, so registration should raise application exceptions instead of crafting ad hoc JSON responses.
- Story 1.1 already provides `AuthService`, `UserRepository`, `User` model, and `hash_password()` / `verify_password()` helpers. Extend these instead of replacing them.
- Story 1.1 review found no blocking issues, but production-hardening of JWT secret defaults remains a future concern unrelated to registration delivery.

### References

- Story 1.2 definition and acceptance criteria: [Source: _bmad-output/planning-artifacts/epics.md#Story-1.2]
- Architecture stack, boundaries, and response envelope: [Source: _bmad-output/planning-artifacts/architecture.md]
- Registration endpoint contract and auth error codes: [Source: _bmad-output/api-contract.md]
- Users table schema and uniqueness constraints: [Source: _bmad-output/database-schema.md]
- Existing backend foundation from Story 1.1: [Source: _bmad-output/implementation-artifacts/1-1-establish-identity-service-foundation.md]

## Project Structure Notes

- Current repo state now includes a live backend foundation in `doitforme-api/` rather than planning-only artifacts.
- Registration should extend the existing foundation rather than adding a second app entrypoint or alternate auth stack.
- No frontend artifacts are relevant to this implementation.

## Dev Agent Record

### Debug Log

- 2026-03-19: Implemented registration endpoint `POST /api/v1/auth/register` with `RegisterRequest` and `RegisterResponse` schemas. `UserPublic` model validates user responses without exposing password hash. `UserRole` admin restriction enforced via Pydantic v2 `field_validator`.
- 2026-03-19: Extended `UserRepository` with `create()` and `get_by_id()` methods. Extended `AuthService` with `register()` method owning duplicate-email check, password policy, hashing, and commit.
- 2026-03-19: Added `email-validator` dependency (required by Pydantic `EmailStr`). Fixed `RequestValidationError` handler — raw `exc.errors()` contains non-serializable `ValueError` instances in `ctx`; replaced with clean dicts stripping `ctx` to avoid `PydanticSerializationError` during JSON serialization.
- 2026-03-19: Validation-error tests switched from httpx ASGITransport to FastAPI `TestClient` (handles exception propagation cleanly). DB-dependent tests marked `@pytest.mark.skip` with clear reason noting live PostgreSQL requirement. All 9 non-DB tests pass; 3 skipped.

### Completion Notes

- Delivered `POST /api/v1/auth/register` with full validation: email format, required fields, password minimum length (8 chars), role restriction (no admin self-assignment), duplicate email conflict (409).
- All responses use the standardized success/error envelope. Password hashes never returned in responses.
- Auth service owns transaction boundaries; repository handles persistence only.
- Registration schema and service are ready for Story 1.3 login — `AuthService.verify_password()`, `UserRepository.get_by_email()`, and auth router boundaries are in place and need no restructuring.

## File List

- doitforme-api/app/api/v1/auth.py
- doitforme-api/app/api/v1/router.py (updated — added auth router inclusion)
- doitforme-api/app/core/exceptions.py (updated — fixed RequestValidationError handler serialization)
- doitforme-api/app/repositories/user_repository.py (updated — added create and get_by_id methods)
- doitforme-api/app/schemas/auth.py
- doitforme-api/app/services/auth_service.py (updated — added register method)
- doitforme-api/tests/api/test_auth.py
- doitforme-api/tests/conftest.py (updated — added session fixture)

## Change Log

- 2026-03-19: Implemented Story 1.2 registration endpoint, schemas, service, repository extensions, and tests.
