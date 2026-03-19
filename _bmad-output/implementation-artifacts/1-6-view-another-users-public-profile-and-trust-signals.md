# Story 1.6: View Another User's Public Profile and Trust Signals

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a platform user,
I want to view another user's public profile, rating, and completed-task stats,
So that I can decide whether to trust them.

## Acceptance Criteria

1. Given a user is allowed to view public trust information for another platform user, when they request another user's public profile, then the API returns the supported public profile fields using the standardized success envelope and includes rating and completed-task statistics needed for trust decisions.
2. Given the requested user does not exist, when the public profile request is processed, then the API returns a not-found error using the standardized error envelope and no internal user information is leaked.
3. Given public profile access must still respect privacy boundaries, when another user's profile is returned, then private or security-sensitive fields are excluded from the response and only the intended public trust-oriented data is exposed.
4. Given Story 1.6 completes the identity and trust epic, when the story is finished, then Epic 1 fully supports user access, self-profile management, and public trust visibility, and tests cover successful public profile retrieval, not-found handling, and exclusion of non-public fields.

## Tasks / Subtasks

- [ ] Define public-profile schemas and response contracts (AC: 1, 2, 3)
  - [ ] Add or extend `app/schemas/user.py` with public-profile response models using `snake_case`
  - [ ] Ensure the public profile contract includes supported trust fields such as name, role, rating, rating count, and completed-task statistics while excluding private fields
- [ ] Implement public-profile retrieval behavior (AC: 1, 2, 3)
  - [ ] Add a public or appropriately authorized users route for fetching another user's profile through the users module
  - [ ] Reuse a shared user service for profile lookup, response shaping, and not-found handling
  - [ ] Return the standardized success envelope through shared response utilities
- [ ] Preserve privacy and trust boundaries (AC: 1, 2, 3)
  - [ ] Exclude private or security-sensitive fields such as email, password-related data, and internal-only attributes from public responses
  - [ ] Keep trust-related fields aligned with the product requirements for rating visibility and completed-task statistics
- [ ] Add focused test coverage for public-profile access (AC: 1, 2, 3, 4)
  - [ ] Add API coverage for successful public profile retrieval
  - [ ] Add API coverage for not-found handling when the requested user does not exist
  - [ ] Add assertions that non-public fields are excluded from the response
- [ ] Validate readiness for later ratings and reputation stories (AC: 1, 4)
  - [ ] Confirm the public-profile response shape stays compatible with later rating-history and reputation stories
  - [ ] Keep trust-signal aggregation boundaries stable for future rating visibility work

## Dev Notes

- Story 1.5 should establish the core user-profile service and response boundaries needed to distinguish self-profile and public-profile behavior.
- Scope boundary: implement another user's public profile and trust-oriented summary visibility only. Do not implement received-ratings history, admin moderation views, or private self-profile updates in this story.
- Keep the modular monolith boundaries intact: router → service → repository. Repositories handle persistence only. Services own response shaping, privacy filtering, and not-found behavior.

### Technical Requirements

- Reuse `app/core/response.py` and centralized exception handling so profile responses stay inside the standardized success/error envelope.
- Keep request and response contracts in `app/schemas/`.
- Keep JSON fields in `snake_case`.

### Architecture Compliance

- Public profile endpoints should live in the users module defined by the architecture.
- The users router must remain thin and delegate profile lookup and privacy filtering to the shared user service.
- The user service should own which fields are public versus private.
- Repository methods should encapsulate persistence only and must not hide commits.

### Library / Framework Requirements

- Continue using FastAPI request handling and centralized exception mapping.
- Reuse SQLAlchemy async session handling and the existing users/ratings persistence model.
- Preserve the standardized success/error envelope across all public-profile responses.

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

- Public-profile reads should be grounded in the existing `users` table and any trust-oriented aggregate fields defined in the schema artifacts.
- The response should include only public trust-oriented data and exclude private or security-sensitive fields.
- Rating visibility in this story is limited to summary trust signals; detailed rating-history views belong to later stories where the product explicitly requires them.

### API Contract Notes

- The contract documents `GET /users/:userId` for profile retrieval; implementation should adapt this into a versioned users endpoint consistent with the final API structure and public/private field boundaries.
- Success responses must use the standardized envelope with `success`, `data`, `error`, and `timestamp`.
- Not-found and privacy-safe failures must continue using the standardized error envelope.
- The contract examples use camelCase, but implementation artifacts in this repo follow final `snake_case` conventions.

### Testing Requirements

- Add or maintain API coverage for:
  - successful public profile retrieval
  - not-found handling
  - exclusion of non-public fields
- Use async-friendly testing patterns consistent with the existing `tests/conftest.py` setup.

### Delivery / Follow-on Story Requirements

- This story should complete Epic 1's public trust visibility without overcommitting to later ratings-detail stories.
- Do not introduce public-profile response shapes that would need rewriting for later reputation and ratings history capabilities.

### Implementation Guardrails

- Do not expose email, password-related data, session fields, internal IDs not meant for clients, or other security-sensitive information in the public profile response unless explicitly required.
- Do not collapse self-profile and public-profile privacy rules into a single overly permissive response shape.
- Do not expand scope into rating-history listing, moderation views, or payment/task-history endpoints.
- Do not bypass the standardized response/error envelope.

### Previous Story Learnings

- Story 1.1 established the shared app structure, exception handling, and response envelope; continue using them rather than creating ad hoc public-profile behavior.
- Story 1.5 is expected to establish the core users service and authenticated profile patterns that this story should reuse.
- Earlier auth stories already established the user identity and trust foundations needed to anchor public-profile visibility.

### References

- Story 1.6 definition and acceptance criteria: [Source: _bmad-output/planning-artifacts/epics.md#Story-1.6]
- Public profile requirement FR5 and trust-related profile FR33/FR34 context: [Source: _bmad-output/prd.md]
- User profile API contract: [Source: _bmad-output/api-contract.md]
- Users service/module architecture guidance: [Source: _bmad-output/planning-artifacts/architecture.md]
- User/profile persistence shape and rating aggregates: [Source: _bmad-output/database-schema.md]
- Self-profile prerequisite context: [Source: _bmad-output/implementation-artifacts/1-5-view-and-update-my-profile.md]

## Dev Agent Record

### Debug Log

- Not started. This artifact was created to make Story 1.6 implementation-ready in the same style as Stories 1.3 through 1.5.

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

- 2026-03-19: Created Story 1.6 implementation artifact from planning, contract, architecture, and schema documents.
