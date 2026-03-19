# Story 1.4: Log Out and Revoke Session Access

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an authenticated user,
I want to log out securely,
So that my session is no longer active on the platform.

## Acceptance Criteria

1. Given an authenticated user has an active session, when they call the logout endpoint with valid authentication context, then the API completes the logout flow successfully and returns a standardized success response.
2. Given the platform contract includes logout behavior, when logout is implemented, then the backend invalidates or revokes the current session according to the chosen token/session strategy, and the resulting behavior is consistent with the architecture's persistent-session expectations.
3. Given a user has logged out successfully, when they attempt to continue using the invalidated session in a way the backend can enforce, then protected access is rejected and the API returns the appropriate authentication error response.
4. Given a logout request is made without valid authentication, when the request is processed, then the API returns an unauthorized error using the standardized error envelope, and no session state is changed for any other user.
5. Given logout is part of the shared auth lifecycle, when the endpoint is implemented, then router logic remains thin and the revocation or invalidation behavior is handled through shared auth services or dependencies, and the flow does not duplicate authorization logic outside the established auth boundary.
6. Given Story 1.4 completes the basic session lifecycle, when the story is finished, then the platform is ready for authenticated profile access stories, and tests cover successful logout, unauthorized logout attempts, and post-logout access rejection where applicable.

## Tasks / Subtasks

- [x] Define logout response contract and endpoint behavior (AC: 1, 4, 5)
  - [x] Reuse `app/schemas/auth.py` for a logout response model that returns the standardized success message without adding unnecessary payload fields
  - [x] Expose `POST /api/v1/auth/logout` under the existing versioned auth router
- [x] Implement session revocation behavior through shared auth layers (AC: 2, 5)
  - [x] Keep `app/api/v1/auth.py` thin and delegate logout orchestration to `AuthService`
  - [x] Reuse `AuthSessionRepository` session lookup and revocation methods rather than duplicating authorization or persistence logic in the router
  - [x] Invalidate only the current authenticated session identified by the access-token context
- [x] Enforce post-logout rejection through the existing auth boundary (AC: 2, 3, 5)
  - [x] Ensure protected access checks reject revoked or otherwise inactive sessions through shared auth dependencies
  - [x] Preserve standardized `INVALID_TOKEN`-style auth failures for rejected inactive-session access where currently covered
- [x] Preserve unauthorized request behavior (AC: 4)
  - [x] Keep missing or malformed authorization header handling inside shared auth dependencies
  - [x] Ensure unauthenticated logout attempts do not revoke any unrelated user session
- [ ] Add focused test coverage for logout lifecycle behavior (AC: 1, 3, 4, 6)
  - [ ] Add API coverage for successful logout with the standardized success envelope
  - [x] Add API coverage for unauthorized logout attempts such as missing or invalid auth headers
  - [ ] Add API or integration coverage that proves reuse of the invalidated session is rejected after logout
  - [x] Add or retain service-level coverage for revoking an active session and rejecting an inactive session
- [x] Validate readiness for profile stories (AC: 3, 6)
  - [x] Confirm the logout implementation leaves the auth boundary stable for upcoming authenticated profile access stories
  - [x] Verify the resulting session lifecycle remains aligned with the persistent-session architecture introduced in Story 1.3

## Dev Notes

- Story 1.3 already established login token issuance, persistent auth-session storage, and the shared auth dependency flow needed to identify the current access-token session.
- Scope boundary: implement logout and current-session revocation only. Do not introduce refresh-token rotation, multi-device session management, or profile endpoint behavior in this story.
- Keep the modular monolith boundaries intact: router → service → repository / dependency. Repositories handle persistence only. Services and auth dependencies own orchestration and enforcement.

### Technical Requirements

- Reuse `app/core/response.py` and centralized exception handling so logout responses stay inside the standardized success/error envelope.
- Keep request and response contracts in `app/schemas/`.
- Continue using the shared JWT decoding and auth dependency path rather than creating a second token-parsing flow for logout.
- Keep JSON fields in `snake_case`.

### Architecture Compliance

- `app/api/v1/auth.py` remains the public auth entrypoint for logout.
- Shared auth dependencies should continue to enforce authenticated access and reject inactive sessions.
- `AuthService` should own session revocation orchestration and transaction completion.
- `AuthSessionRepository` should encapsulate session lookup and revocation persistence only.
- Do not bypass the service layer or duplicate authorization logic in the route handler.

### Library / Framework Requirements

- Continue using FastAPI dependency injection for authenticated request handling.
- Keep failure paths flowing through the centralized exception handling path so the standardized envelope is preserved.
- Reuse SQLAlchemy async session handling and the existing auth/session persistence model.

### File Structure Requirements

- Existing files expected to be extended:
  - `doitforme-api/app/api/v1/auth.py`
  - `doitforme-api/app/api/deps.py`
  - `doitforme-api/app/repositories/auth_session_repository.py`
  - `doitforme-api/app/services/auth_service.py`
  - `doitforme-api/tests/api/test_auth.py`
  - `doitforme-api/tests/services/test_auth_service.py`
- New files are not expected unless logout-specific tests or support artifacts are strictly required.

### Data / Persistence Notes

- Logout should operate on the persisted auth-session model introduced for login session tracking.
- The current authenticated session should be identified from the access token's `jti` / token context and revoked in persistence.
- Revocation should affect only the current session and must not mutate unrelated user sessions.
- Post-logout enforcement should treat revoked or inactive sessions as unusable for protected access.

### API Contract Notes

- Logout endpoint from `_bmad-output/api-contract.md` is `POST /auth/logout`, which under the implemented versioned API should be exposed as `POST /api/v1/auth/logout`.
- Request authentication should come from `Authorization: Bearer <jwt_token>` using the established auth dependency flow.
- Success responses must use the standardized envelope:
  - `success: true`
  - `data: { "message": "Successfully logged out" }`
  - `error: null`
  - `timestamp: ISO-8601`
- Unauthorized or invalid-token responses must continue using the standardized error envelope.

### Testing Requirements

- Add or maintain API coverage for:
  - successful logout
  - missing authorization header
  - invalid authorization header
  - post-logout access rejection where enforceable through current backend routes
- Preserve service-level coverage for revoking an active session and rejecting logout for inactive sessions.
- Use async-friendly testing patterns consistent with the existing `tests/conftest.py` setup.

### Delivery / Follow-on Story Requirements

- This story should complete the basic auth session lifecycle so Story 1.5 can build authenticated profile access on top of a stable shared auth boundary.
- Do not introduce auth abstractions or response shapes that would need rewriting for profile endpoints.

### Implementation Guardrails

- Do not duplicate token parsing or authorization logic in the router.
- Do not revoke sessions other than the one associated with the current authenticated access token.
- Do not broaden scope into refresh-token rotation, session listing, or account/profile features.
- Do not bypass the standardized response/error envelope.

### Previous Story Learnings

- Story 1.1 established the shared response, exception, and app structure foundations; continue using them rather than creating ad hoc logout behavior.
- Story 1.2 established the public auth router and `AuthService` boundary; logout should extend that same structure.
- Story 1.3 established persistent session creation and token payload expectations needed for current-session revocation; build on those boundaries without restructuring.

### References

- Story 1.4 definition and acceptance criteria: [Source: _bmad-output/planning-artifacts/epics.md#Story-1.4]
- Logout contract: [Source: _bmad-output/api-contract.md]
- Product requirement FR6: [Source: _bmad-output/prd.md]
- Readiness mapping for Epic 1 Story 1.4: [Source: _bmad-output/planning-artifacts/implementation-readiness-report-2026-03-19.md]
- Prior auth-session and login groundwork: [Source: _bmad-output/implementation-artifacts/1-3-log-in-and-receive-session-tokens.md]

## Dev Agent Record

### Debug Log

- 2026-03-19: Documented the existing logout implementation already present in `app/api/v1/auth.py`, `app/services/auth_service.py`, `app/api/deps.py`, and `app/repositories/auth_session_repository.py`.
- 2026-03-19: Recorded current test evidence: API validation coverage exists for missing and malformed auth headers, service-level coverage exists for active/inactive logout behavior, and an API check exists for expired-session rejection.
- 2026-03-19: Review context indicates Story 1.4 remains in `review` because clear end-to-end evidence is still missing for successful logout response coverage and post-logout token reuse rejection.

### Completion Notes

- Delivered `POST /api/v1/auth/logout` with a thin auth router delegating to `AuthService.logout` and standardized success/error envelopes.
- Shared auth dependencies reject inactive sessions, preserving the established auth boundary for protected requests and follow-on profile stories.
- Story remains in review because the documentation and prior review evidence still call for stronger end-to-end proof of successful logout response coverage and post-logout rejection behavior.

## File List

- doitforme-api/app/api/v1/auth.py
- doitforme-api/app/api/deps.py
- doitforme-api/app/repositories/auth_session_repository.py
- doitforme-api/app/services/auth_service.py
- doitforme-api/tests/api/test_auth.py
- doitforme-api/tests/services/test_auth_service.py

## Change Log

- 2026-03-19: Created Story 1.4 implementation artifact from the planning and contract documents.
- 2026-03-19: Updated Story 1.4 artifact to reflect the current implemented-but-in-review logout state.
