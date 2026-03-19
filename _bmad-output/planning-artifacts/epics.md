---
stepsCompleted: ["step-01-extraction-confirmed", "step-02-epics-approved"]
inputDocuments: ["_bmad-output/prd.md", "_bmad-output/planning-artifacts/architecture.md"]
---

# DoItForMe - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for DoItForMe, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: A new user can register with email and password
FR2: A registered user can log in with email and password
FR3: A logged-in user can view their profile (name, rating, completed tasks count)
FR4: A user can update their profile information
FR5: A user can view another user's profile with their stats and ratings
FR6: A user can log out and invalidate their session
FR7: A task poster can create a new task with title, description, location, and initial price offer
FR8: A task poster can view all their posted tasks
FR9: A task poster can view details of a specific task
FR10: A task can display its current status (open, in-progress, completed, cancelled)
FR11: A task poster can cancel an open task
FR12: A task poster can mark a task as completed (triggering payment release)
FR13: A task performer can view a list of available tasks
FR14: Tasks are filtered by proximity to the performer's location (distance-based)
FR15: Tasks display essential information: title, location distance, posted by, current price
FR16: A performer can view detailed information about a task before accepting
FR17: A task performer can accept a task at the posted price
FR18: A task performer can propose a different price instead of accepting the posted price
FR19: A task poster can view proposals/counter-offers on their task
FR20: A task poster can accept or reject a performer's counter-offer
FR21: Once a proposal is accepted, the task status changes to "accepted" and the performer is locked in
FR22: Two users on an accepted task can send messages to each other
FR23: Message history is visible chronologically within a task
FR24: Users can view all active conversations (tasks with accepted performers)
FR25: Messages appear in real-time or near-real-time for both parties
FR26: When a task is accepted, payment is held in a simulated escrow
FR27: The payment amount is displayed clearly to both parties
FR28: When a task is marked complete, payment is released to the performer
FR29: A user can view their payment history (earnings or spent)
FR30: Admin can manually release or hold payment if needed
FR31: After a task is completed, the task poster can rate the performer (1-5 stars with optional comment)
FR32: After a task is completed, the performer can rate the task poster (1-5 stars with optional comment)
FR33: A user's profile displays their average rating across all completed tasks
FR34: A user can view all ratings they've received
FR35: Admin can view total number of tasks posted
FR36: Admin can view number of completed tasks and completion rate
FR37: Admin can view total number of registered users
FR38: Admin can view a list of all users
FR39: Admin can view a list of all tasks with their statuses
FR40: Admin can view task details and associated messages (for moderation)
FR41: Admin can manually adjust or release a payment
FR42: Admin can view platform statistics (completion rate, avg rating, active users)

### NonFunctional Requirements

NFR1: Task listings load within 2 seconds
NFR2: Chat messages display within 1 second of sending
NFR3: Location-based task filtering completes within 2 seconds
NFR4: User authentication (login/signup) completes within 3 seconds
NFR5: The system supports at least 50 concurrent users without degradation
NFR6: All user passwords are hashed and never stored in plain text
NFR7: All API requests require valid JWT authentication token
NFR8: User can only view/modify their own tasks and payments
NFR9: Admin endpoints are restricted and cannot be accessed by regular users
NFR10: Chat messages are not visible to users not involved in the task
NFR11: Payment data is isolated per user (users cannot view others' payment history)
NFR12: All sensitive API communications use HTTPS/SSL encryption
NFR13: System architecture supports horizontal scaling (multiple backend instances)
NFR14: Database queries are optimized to handle 10,000+ tasks
NFR15: Real-time messaging can handle 100+ concurrent chat sessions
NFR16: Location-based queries are indexed for fast response times

### Additional Requirements

- Backend stack must use Python with FastAPI and a manual FastAPI scaffold managed via `uv`
- PostgreSQL is the primary database with SQLAlchemy async, asyncpg, and Alembic migrations
- REST API must be versioned under `/api/v1`
- OpenAPI/Swagger documentation must be available and aligned with FastAPI docs generation
- Real-time behavior is implemented with polling for MVP, not WebSockets
- Authentication uses JWT with RBAC + resource ownership checks for roles `poster`, `performer`, and `admin`
- Password hashing uses `passlib` + `bcrypt`
- Rate limiting uses `slowapi` with stricter rules for auth and polling endpoints
- Secrets/configuration use `pydantic-settings` and environment variables
- API responses must use the standardized success/error envelope documented in the architecture
- Codebase must follow modular boundaries across routers, services, repositories, schemas, models, and core utilities
- Routers must remain thin; service layer owns business logic and transaction boundaries
- Repositories are the only layer allowed to directly query ORM persistence
- Dockerized local/prod deployment and Gunicorn + Uvicorn workers are required deployment assumptions
- Health/readiness endpoints, structured logging, and CI validation are part of the implementation baseline
- Project structure must follow the defined `app/api/v1`, `app/core`, `app/db`, `app/models`, `app/schemas`, `app/services`, `app/repositories`, and `tests` organization
- Epic 1 Story 1 must initialize the FastAPI project scaffold, core config, DB session management, Alembic, and auth foundations before feature stories

### UX Design Requirements

No UX design document applies to this backend-only project.

### FR Coverage Map

FR1: Epic 1 - User can register
FR2: Epic 1 - User can log in
FR3: Epic 1 - User can view own profile
FR4: Epic 1 - User can update own profile
FR5: Epic 1 - User can view another user's profile
FR6: Epic 1 - User can log out
FR7: Epic 2 - Poster can create a task
FR8: Epic 2 - Poster can view posted tasks
FR9: Epic 2 - Poster can view task details
FR10: Epic 2 - Task status is visible
FR11: Epic 2 - Poster can cancel open task
FR12: Epic 4 - Poster can mark task completed
FR13: Epic 2 - Performer can view available tasks
FR14: Epic 2 - Tasks are filtered by proximity
FR15: Epic 2 - Task listings show essential info
FR16: Epic 2 - Performer can view task details before accepting
FR17: Epic 3 - Performer can accept a task at posted price
FR18: Epic 3 - Performer can propose a counter-price
FR19: Epic 3 - Poster can view proposals
FR20: Epic 3 - Poster can accept or reject counter-offers
FR21: Epic 3 - Accepted proposal locks in performer and updates status
FR22: Epic 4 - Accepted task participants can send messages
FR23: Epic 4 - Message history is visible chronologically
FR24: Epic 4 - Users can view active conversations
FR25: Epic 4 - Messages appear in near-real-time
FR26: Epic 5 - Payment is held in simulated escrow when task is accepted
FR27: Epic 5 - Payment amount is clearly displayed
FR28: Epic 5 - Payment is released when task is completed
FR29: Epic 5 - User can view payment history
FR30: Epic 5 - Admin can manually hold or release payment
FR31: Epic 6 - Poster can rate performer after completion
FR32: Epic 6 - Performer can rate poster after completion
FR33: Epic 6 - User profile displays average rating
FR34: Epic 6 - User can view ratings received
FR35: Epic 6 - Admin can view total tasks posted
FR36: Epic 6 - Admin can view completed tasks and completion rate
FR37: Epic 6 - Admin can view total registered users
FR38: Epic 6 - Admin can view all users
FR39: Epic 6 - Admin can view all tasks and statuses
FR40: Epic 6 - Admin can view task details and messages
FR41: Epic 6 - Admin can manually adjust or release payment
FR42: Epic 6 - Admin can view platform statistics

## Epic List

### Epic 1: User Access & Identity
Users can register, sign in, manage their profile, and establish identity and trust on the platform.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6

### Epic 2: Task Posting & Discovery
Task posters can publish tasks and performers can discover nearby work opportunities with enough context to decide whether to engage.
**FRs covered:** FR7, FR8, FR9, FR10, FR11, FR13, FR14, FR15, FR16

### Epic 3: Task Negotiation & Assignment
Posters and performers can agree on who will do a task and at what price, resulting in an accepted assignment.
**FRs covered:** FR17, FR18, FR19, FR20, FR21

### Epic 4: Task Communication & Execution
Once a task is accepted, both parties can communicate, track task progress, and move the task toward completion.
**FRs covered:** FR12, FR22, FR23, FR24, FR25

### Epic 5: Simulated Payments & Completion
The platform can hold, release, and display simulated payments and payment history around task completion.
**FRs covered:** FR26, FR27, FR28, FR29, FR30

### Epic 6: Ratings, Reputation & Admin Oversight
Users can build reputation after completed work, while admins can monitor and manage platform health and interventions.
**FRs covered:** FR31, FR32, FR33, FR34, FR35, FR36, FR37, FR38, FR39, FR40, FR41, FR42

<!-- Repeat for each epic in epics_list (N = 1, 2, 3...) -->

## Epic 1: User Access & Identity

Users can register, sign in, manage their profile, and establish identity and trust on the platform.

<!-- Repeat for each story (M = 1, 2, 3...) within epic N -->

### Story 1.1: Initialize FastAPI Service Foundation

As a developer,
I want the backend service scaffolded with configuration, database connectivity, migrations, and shared API conventions,
So that all future identity features can be built consistently.

**Acceptance Criteria:**

**Given** the repository is still at the pre-implementation stage
**When** the service foundation is created
**Then** a FastAPI project scaffold exists using the agreed Python + FastAPI + `uv` setup
**And** the project structure matches the architecture document for `app/api/v1`, `app/core`, `app/db`, `app/models`, `app/schemas`, `app/services`, `app/repositories`, and `tests`

**Given** the service foundation is being established
**When** application configuration is implemented
**Then** environment-driven settings are loaded through `pydantic-settings`
**And** local configuration can be supplied through `.env` without hardcoding secrets

**Given** the service foundation includes persistence setup
**When** the database layer is prepared
**Then** PostgreSQL connectivity is configured with SQLAlchemy async and `asyncpg`
**And** an async session pattern is available for future repositories and services

**Given** schema evolution must be controlled from the start
**When** migrations are initialized
**Then** Alembic is configured in the project
**And** the project is ready to create and run migrations for only the tables needed by future stories

**Given** future endpoints must behave consistently
**When** shared API behavior is established
**Then** the application includes the standard API success/error response envelope and centralized exception handling
**And** the main API router is versioned under `/api/v1`

**Given** authentication is part of the agreed architecture
**When** the initial security foundation is created
**Then** the project includes the base security utilities needed for password hashing and JWT token support
**And** the full registration/login behavior remains deferred to later stories in this epic

**Given** implementation quality must support future agent work
**When** the foundation story is completed
**Then** the codebase includes the initial test configuration and health/readiness endpoints
**And** the foundation is sufficient for Story 1.2 to implement user registration without restructuring the project

### Story 1.2: Register User Account

As a new user,
I want to create an account with email and password,
So that I can join the platform.

**Acceptance Criteria:**

**Given** a visitor does not yet have an account
**When** they submit a valid registration request with required identity fields, role, email, and password
**Then** a new user record is created in the database
**And** the password is stored only as a secure hash

**Given** a registration request is received
**When** the submitted email already belongs to an existing user
**Then** the API rejects the request with a conflict-style error response
**And** no duplicate account is created

**Given** a registration request is received
**When** required fields are missing or the payload format is invalid
**Then** the API returns a validation error using the standardized error envelope
**And** no user record is created

**Given** a registration request is received
**When** the password does not meet the minimum security rules defined by the implementation
**Then** the API rejects the request with a clear validation error
**And** the response does not expose internal security logic beyond what the client needs

**Given** a registration succeeds
**When** the user record is returned or acknowledged by the API
**Then** the response excludes the password hash and any secret fields
**And** the returned payload follows the standardized success envelope

**Given** role-aware authorization is part of the platform architecture
**When** a new user registers
**Then** the created account is assigned a valid supported role
**And** unsupported or unauthorized roles cannot be self-assigned through the public registration flow

**Given** registration is an identity foundation story
**When** Story 1.2 is completed
**Then** the system supports the next login story without restructuring the user domain
**And** tests cover successful registration, duplicate email rejection, and invalid payload handling

### Story 1.3: Log In and Receive Session Tokens

As a registered user,
I want to log in with my credentials and receive authentication tokens,
So that I can access protected platform features.

**Acceptance Criteria:**

**Given** a registered user has a valid account
**When** they submit the correct email and password
**Then** the API authenticates the user successfully
**And** returns the login response using the standardized success envelope

**Given** a login succeeds
**When** authentication tokens are issued
**Then** the response includes the token data needed for authenticated requests and session continuation
**And** the issued token contents are aligned with the agreed JWT-based architecture

**Given** the platform uses role-aware authorization
**When** a user logs in successfully
**Then** the authenticated identity includes the user's supported role and user identifier
**And** the token payload is sufficient for downstream authorization checks without exposing sensitive data

**Given** a login request is received
**When** the email does not exist or the password is incorrect
**Then** the API rejects the request with an authentication error
**And** the response does not reveal which credential was invalid

**Given** a login request is received
**When** the payload is malformed or required fields are missing
**Then** the API returns a validation error using the standardized error envelope
**And** no authentication tokens are issued

**Given** authentication is a security-sensitive flow
**When** login is implemented
**Then** password verification uses the shared secure hashing utilities established earlier
**And** the implementation does not duplicate hashing logic ad hoc inside routers

**Given** Epic 1 requires persistent session behavior in the backend contract
**When** Story 1.3 is completed
**Then** the authentication flow is ready for subsequent logout and protected-profile stories
**And** tests cover successful login, invalid credentials, and invalid request payloads

<!-- End story repeat -->
