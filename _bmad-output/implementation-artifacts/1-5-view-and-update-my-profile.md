# Story 1.5: View and Update My Profile

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an authenticated user,
I want to view and update my profile information,
So that my account details stay accurate.

## Acceptance Criteria

1. Given an authenticated user has a valid session, when they request their own profile, then the API returns their profile details using the standardized success envelope and includes the trust-related fields required by the product such as name, role, rating, and completed-task count.
2. Given an authenticated user submits valid changes to editable profile fields, when the update request is processed, then the user's profile is updated successfully and non-editable or protected fields remain unchanged.
3. Given a profile update request contains invalid or malformed data, when the API validates the payload, then the request is rejected with a validation error using the standardized error envelope and no partial invalid update is persisted.
4. Given profile access is user-scoped, when a user attempts to modify another user's profile through the self-profile flow, then the API rejects the request according to the ownership and authorization rules and no unauthorized profile change occurs.
5. Given Epic 1 requires profile trust information to support later marketplace flows, when Story 1.5 is completed, then user profile read and update capabilities are available for authenticated use, and tests cover successful profile retrieval, successful profile update, invalid payload handling, and unauthorized modification attempts.

## Tasks / Subtasks

- [ ] Define self-profile schemas and response contracts (AC: 1, 2, 3)
  - [ ] Add or extend `app/schemas/user.py` with self-profile read/update request and response models using `snake_case`
  - [ ] Ensure self-profile responses include supported trust-related fields such as rating, rating count, and completed-task count without exposing security-sensitive data
- [ ] Implement authenticated self-profile retrieval (AC: 1, 4, 5)
  - [ ] Add a thin authenticated self-profile route under `app/api/v1/users.py` or the canonical users router defined by the architecture
  - [ ] Reuse the shared auth dependency path so self-profile access is derived from the current authenticated user rather than arbitrary user identifiers
  - [ ] Return the standardized success envelope through shared response utilities
- [ ] Implement authenticated self-profile update behavior (AC: 2, 3, 4)
  - [ ] Restrict updates to editable profile fields only
  - [ ] Prevent modification of protected fields such as identity, role, ratings, and other trust statistics through the self-update payload
  - [ ] Keep persistence orchestration inside the service layer and leave repositories persistence-only
- [ ] Preserve ownership and authorization rules (AC: 4)
  - [ ] Ensure the self-profile flow cannot be used to modify another user's profile
  - [ ] Keep authorization and ownership enforcement inside the established auth and service boundaries
- [ ] Add focused test coverage for authenticated profile flows (AC: 1, 2, 3, 4, 5)
  - [ ] Add API coverage for successful self-profile retrieval
  - [ ] Add API coverage for successful self-profile update
  - [ ] Add API coverage for invalid payload handling
  - [ ] Add API or service coverage for unauthorized modification attempts or protected-field update rejection
- [ ] Validate readiness for public-profile trust stories (AC: 1, 5)
  - [ ] Confirm the self-profile response shape stays compatible with upcoming public-profile and trust-signal stories
  - [ ] Keep user-domain boundaries stable for Story 1.6 and later rating visibility work

## Dev Notes

- Story 1.4 completed the authenticated session lifecycle and leaves a stable auth boundary for authenticated profile access.
- Scope boundary: implement authenticated self-profile read and update only. Do not implement public other-user profile access, received-ratings listing, or broader trust-history endpoints in this story.
- Keep the modular monolith boundaries intact: router → service → repository / dependency. Repositories handle persistence only. Services own orchestration, authorization-aware decisions, and transaction boundaries.

### Technical Requirements

- Reuse `app/core/response.py` and centralized exception handling so profile responses stay inside the standardized success/error envelope.
- Keep request and response contracts in `app/schemas/`.
- Continue using the shared authenticated dependency path introduced by the auth stories.
- Keep JSON fields in `snake_case`.

### Architecture Compliance

- Profile endpoints should live in the users module defined by the architecture, not inside the auth router.
- The users router must remain thin and delegate retrieval/update orchestration to a shared user service.
- Ownership enforcement for the self-profile flow should rely on the authenticated user context, not client-supplied ownership claims.
- Repository methods should encapsulate persistence only and must not hide commits.

### Library / Framework Requirements

- Continue using FastAPI dependency injection for authenticated request handling.
- Keep validation and failure paths flowing through the centralized exception handling path so the standardized envelope is preserved.
- Reuse SQLAlchemy async session handling and the existing users/auth persistence model.

### File Structure Requirements

- Existing files expected to be extended:
  - `doitforme-api/app/api/v1/router.py`
  - `doitforme-api/app/api/v1/users.py`
  - `doitforme-api/app/repositories/user_repository.py`
  - `doitforme-api/app/services/user_service.py`
  - `doitforme-api/tests/api/test_users.py`
  - `doitforme-api/tests/services/test_user_service.py`
- Additional schema support is likely required in:
  - `doitforme-api/app/schemas/user.py`

### Data / Persistence Notes

- Self-profile reads should be grounded in the existing `users` table and its profile fields.
- Trust-oriented fields such as rating, rating count, and completed-task count should be returned where supported by the current schema and product requirements.
- Update behavior must preserve protected identity and trust fields while allowing only the supported editable profile fields.

### API Contract Notes

- The contract documents `GET /users/:userId` and `PUT /users/:userId`; implementation should adapt this into a secure self-profile flow consistent with ownership/auth rules and the versioned API structure.
- Success responses must use the standardized envelope with `success`, `data`, `error`, and `timestamp`.
- Error responses must continue using the standardized error envelope.
- The contract examples use camelCase, but implementation artifacts in this repo follow final `snake_case` conventions.

### Testing Requirements

- Add or maintain API coverage for:
  - successful self-profile retrieval
  - successful self-profile update
  - invalid payload handling
  - unauthorized modification or protected-field update rejection
- Use async-friendly testing patterns consistent with the existing `tests/conftest.py` setup.

### Delivery / Follow-on Story Requirements

- This story should prepare Story 1.6 by establishing a stable user service and profile response boundary for public-profile reads.
- Do not introduce response shapes or profile abstractions that would need rewriting for public trust visibility.

### Implementation Guardrails

- Do not expose private or security-sensitive fields in self-profile responses beyond what the product explicitly requires.
- Do not let the self-profile update flow modify another user's record.
- Do not allow updates to protected fields such as role, rating, rating count, completed-task count, password hash, or internal identifiers through the public payload.
- Do not bypass the standardized response/error envelope.

### Previous Story Learnings

- Story 1.1 established the shared app structure, exception handling, and response envelope; continue using them rather than creating ad hoc profile behavior.
- Story 1.2 and Story 1.3 established the auth and user-domain foundations needed for authenticated user identity.
- Story 1.4 leaves the auth boundary ready for authenticated profile access without restructuring.

### References

- Story 1.5 definition and acceptance criteria: [Source: _bmad-output/planning-artifacts/epics.md#Story-1.5]
- Profile-related requirements FR3 and FR4: [Source: _bmad-output/prd.md]
- User profile API contract: [Source: _bmad-output/api-contract.md]
- Users service/module architecture guidance: [Source: _bmad-output/planning-artifacts/architecture.md]
- User/profile persistence shape and trust fields: [Source: _bmad-output/database-schema.md]
- Auth/session prerequisite context: [Source: _bmad-output/implementation-artifacts/1-4-log-out-and-revoke-session-access.md]

## Dev Agent Record

### Debug Log

- Not started. This artifact was created to make Story 1.5 implementation-ready in the same style as Stories 1.3 and 1.4.

### Completion Notes

- No implementation has been recorded in this artifact yet.

## File List

- Planned implementation files to be confirmed during development:
  - doitforme-api/app/api/v1/router.py
  - doitforme-api/app/api/v1/users.py
  - doitforme-api/app/repositories/user_repository.py
  - doitforme-api/app/services/user_service.py
  - doitforme-api/app/schemas/user.py
  - doitforme-api/tests/api/test_users.py
  - doitforme-api/tests/services/test_user_service.py

## Change Log

- 2026-03-19: Created Story 1.5 implementation artifact from planning, contract, architecture, and schema documents.
