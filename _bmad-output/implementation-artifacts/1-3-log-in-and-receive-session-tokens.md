# Story 1.3: Log In and Receive Session Tokens

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a registered user,
I want to log in with my credentials and receive authentication tokens,
So that I can access protected platform features.

## Acceptance Criteria

1. Given a registered user has a valid account, when they submit the correct email and password, then the API authenticates the user successfully and returns the login response using the standardized success envelope.
2. Given a login succeeds, when authentication tokens are issued, then the response includes the token data needed for authenticated requests and session continuation, and the issued token contents are aligned with the agreed JWT-based architecture.
3. Given the platform uses role-aware authorization, when a user logs in successfully, then the authenticated identity includes the user's supported role and user identifier, and the token payload is sufficient for downstream authorization checks without exposing sensitive data.
4. Given a login request is received, when the email does not exist or the password is incorrect, then the API rejects the request with an authentication error, and the response does not reveal which credential was invalid.
5. Given a login request is received, when the payload is malformed or required fields are missing, then the API returns a validation error using the standardized error envelope, and no authentication tokens are issued.
6. Given authentication is a security-sensitive flow, when login is implemented, then password verification uses the shared secure hashing utilities established earlier, and the implementation does not duplicate hashing logic ad hoc inside routers.
7. Given Epic 1 requires persistent session behavior in the backend contract, when Story 1.3 is completed, then the authentication flow is ready for subsequent logout and protected-profile stories, and tests cover successful login, invalid credentials, and invalid request payloads.

## Tasks / Subtasks

- [x] Define login schemas and response contracts (AC: 1, 2, 3, 5)
  - [x] Extend `app/schemas/auth.py` with login request and response models using `snake_case`
  - [x] Return token fields and public user data without exposing password hash or other secret persistence fields
- [x] Implement login service logic (AC: 1, 2, 3, 4, 6)
  - [x] Reuse `UserRepository.get_by_email()` for user lookup
  - [x] Verify passwords through the shared `verify_password()` security helper
  - [x] Issue JWT token data through the shared token creation utility instead of ad hoc router logic
  - [x] Return a non-revealing `INVALID_CREDENTIALS` error for both unknown email and wrong password paths
- [x] Expose the login API endpoint (AC: 1, 2, 4, 5)
  - [x] Extend `app/api/v1/auth.py` with a thin `/auth/login` route under `/api/v1`
  - [x] Preserve the standardized success/error response envelope through shared response/exception utilities
- [x] Add tests for login behavior (AC: 4, 5, 7)
  - [x] Add validation tests for malformed login payloads
  - [x] Add successful login coverage for DB-backed flow
  - [x] Add invalid-credential coverage for wrong-password and unknown-email paths with the same client-facing error message
  - [x] Add service-level token issuance tests without requiring database access
- [x] Validate follow-on readiness (AC: 2, 3, 7)
  - [x] Confirm token payload includes user identifier, email, and role for downstream authorization
  - [x] Keep the auth boundary ready for logout and protected-profile stories without restructuring

## Dev Notes

- Story 1.2 already established the public auth router module, registration schemas, the `AuthService` boundary, and `UserRepository.get_by_email()` lookup behavior.
- Scope boundary: implement login only. Do not implement logout revocation, protected profile endpoints, or broader session invalidation behavior in this story.
- Reuse the existing modular monolith boundaries: router → service → repository.

### Technical Requirements

- Use `app/core/security.py` for password verification and JWT generation.
- Keep request/response contracts in `app/schemas/`.
- Continue using the shared success/error envelope utilities and exception mapping.
- Keep JSON fields in `snake_case`.

### Architecture Compliance

- `app/api/v1/auth.py` remains the public auth entrypoint.
- `AuthService` owns credential verification and token issuance.
- `UserRepository` remains persistence-only.
- Token payload must support downstream authorization checks with `sub`, `email`, and `role`.

### Testing Requirements

- Add API validation coverage for malformed login requests.
- Add successful login and invalid-credential API coverage using the existing async test setup.
- Add service-level coverage for successful token issuance and invalid-credential failures.

### References

- Story 1.3 definition and acceptance criteria: [Source: _bmad-output/planning-artifacts/epics.md#Story-1.3]
- Login contract and auth error code: [Source: _bmad-output/api-contract.md]
- Existing auth boundaries and follow-on expectations: [Source: _bmad-output/implementation-artifacts/1-2-register-user-account.md]

## Dev Agent Record

### Debug Log

- 2026-03-19: Extended the auth schemas, service, and router to support `POST /api/v1/auth/login` using the existing password verification and JWT helpers.
- 2026-03-19: Added validation tests for malformed login payloads, DB-backed API login tests (kept consistent with the existing skipped-live-DB pattern), and service-level token issuance tests that run without a database.
- 2026-03-19: Python LSP diagnostics could not be executed in this environment because `basedpyright-langserver` is not installed.

### Completion Notes

- Delivered `POST /api/v1/auth/login` with standardized success/error envelopes and non-revealing invalid-credential handling.
- Login now issues token data using the shared JWT helper and preserves the auth module boundaries needed by upcoming logout and protected-profile stories.
- Added service-level tests that verify token issuance and credential rejection paths without requiring PostgreSQL.

## File List

- doitforme-api/app/api/v1/auth.py
- doitforme-api/app/schemas/auth.py
- doitforme-api/app/services/auth_service.py
- doitforme-api/tests/api/test_auth.py
- doitforme-api/tests/services/test_auth_service.py

## Change Log

- 2026-03-19: Implemented Story 1.3 login endpoint, token issuance flow, and test coverage.
