---
stepsCompleted: ["step-01-extraction-confirmed", "step-02-epics-approved", "correct-course-2026-03-19"]
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

### Story 1.1: Establish Identity Service Foundation

As a new platform user,
I want the identity service foundation to be available,
So that registration and login can be delivered on a stable backend base.

**Implements:** FR1, FR2 (enabling foundation)

**Acceptance Criteria:**

**Given** Epic 1 begins with identity capabilities
**When** the first story is implemented
**Then** the backend provides the minimum service foundation required to support registration and login
**And** that foundation follows the agreed FastAPI architecture and project structure

**Given** identity features require configuration and persistence support
**When** the foundation is established
**Then** environment-based configuration, database session management, and migration support are available
**And** only the minimum infrastructure needed for identity features is introduced

**Given** future identity endpoints must behave consistently
**When** the shared application layer is prepared
**Then** API versioning, standardized response/error handling, and base security utilities are available
**And** registration and login behavior remains deferred to subsequent stories

**Given** the story should enable immediate follow-on user value
**When** Story 1.1 is completed
**Then** Story 1.2 can implement user registration without restructuring the project
**And** Story 1.3 can implement login using the same shared foundation

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

### Story 1.4: Log Out and Revoke Session Access

As an authenticated user,
I want to log out securely,
So that my session is no longer active on the platform.

**Acceptance Criteria:**

**Given** an authenticated user has an active session
**When** they call the logout endpoint with valid authentication context
**Then** the API completes the logout flow successfully
**And** returns a standardized success response

**Given** the platform contract includes logout behavior
**When** logout is implemented
**Then** the backend invalidates or revokes the current session according to the chosen token/session strategy
**And** the resulting behavior is consistent with the architecture's persistent-session expectations

**Given** a user has logged out successfully
**When** they attempt to continue using the invalidated session in a way the backend can enforce
**Then** protected access is rejected
**And** the API returns the appropriate authentication error response

**Given** a logout request is made without valid authentication
**When** the request is processed
**Then** the API returns an unauthorized error using the standardized error envelope
**And** no session state is changed for any other user

**Given** logout is part of the shared auth lifecycle
**When** the endpoint is implemented
**Then** router logic remains thin and the revocation/invalidation behavior is handled through shared auth services or dependencies
**And** the flow does not duplicate authorization logic outside the established auth boundary

**Given** Story 1.4 completes the basic session lifecycle
**When** the story is finished
**Then** the platform is ready for authenticated profile access stories
**And** tests cover successful logout, unauthorized logout attempts, and post-logout access rejection where applicable

### Story 1.5: View and Update My Profile

As an authenticated user,
I want to view and update my profile information,
So that my account details stay accurate.

**Acceptance Criteria:**

**Given** an authenticated user has a valid session
**When** they request their own profile
**Then** the API returns their profile details using the standardized success envelope
**And** the response includes the trust-related fields required by the product such as name, role, rating, and completed-task count

**Given** an authenticated user submits valid changes to editable profile fields
**When** the update request is processed
**Then** the user's profile is updated successfully
**And** non-editable or protected fields remain unchanged

**Given** a profile update request contains invalid or malformed data
**When** the API validates the payload
**Then** the request is rejected with a validation error using the standardized error envelope
**And** no partial invalid update is persisted

**Given** profile access is user-scoped
**When** a user attempts to modify another user's profile through the self-profile flow
**Then** the API rejects the request according to the ownership and authorization rules
**And** no unauthorized profile change occurs

**Given** Epic 1 requires profile trust information to support later marketplace flows
**When** Story 1.5 is completed
**Then** user profile read/update capabilities are available for authenticated use
**And** tests cover successful profile retrieval, successful profile update, invalid payload handling, and unauthorized modification attempts

### Story 1.6: View Another User's Public Profile and Trust Signals

As a platform user,
I want to view another user's public profile, rating, and completed-task stats,
So that I can decide whether to trust them.

**Acceptance Criteria:**

**Given** a user is allowed to view public trust information for another platform user
**When** they request another user's public profile
**Then** the API returns the supported public profile fields using the standardized success envelope
**And** the response includes rating and completed-task statistics needed for trust decisions

**Given** the requested user does not exist
**When** the public profile request is processed
**Then** the API returns a not-found error using the standardized error envelope
**And** no internal user information is leaked

**Given** public profile access must still respect privacy boundaries
**When** another user's profile is returned
**Then** private or security-sensitive fields are excluded from the response
**And** only the intended public trust-oriented data is exposed

**Given** Story 1.6 completes the identity and trust epic
**When** the story is finished
**Then** Epic 1 fully supports user access, self-profile management, and public trust visibility
**And** tests cover successful public profile retrieval, not-found handling, and exclusion of non-public fields

## Epic 2: Task Posting & Discovery

Task posters can publish tasks and performers can discover nearby work opportunities with enough context to decide whether to engage.

### Story 2.1: Create a New Task

As a task poster,
I want to create a new task with title, description, location, and initial price,
So that I can request help from nearby performers.

**Acceptance Criteria:**

**Given** an authenticated poster submits a valid task payload
**When** the create task request is processed
**Then** a new task is stored with its required core fields and default open status
**And** the response returns the created task using the standardized success envelope

**Given** a create task request is missing required fields or contains invalid values
**When** validation occurs
**Then** the API rejects the request with a validation error
**And** no task record is created

**Given** task creation is subject to platform limits
**When** a user exceeds the allowed task creation threshold
**Then** the API rejects the request according to the rate-limit and business rules
**And** the user receives an appropriate error response

### Story 2.2: View My Posted Tasks and Task Details

As a task poster,
I want to view my posted tasks and inspect individual task details,
So that I can manage the work I have requested.

**Acceptance Criteria:**

**Given** an authenticated poster has created one or more tasks
**When** they request their task list
**Then** the API returns the tasks associated with that poster
**And** each task includes the current status and key summary fields

**Given** an authenticated poster requests a specific task they own
**When** the detail request is processed
**Then** the API returns the task details successfully
**And** the response follows the standardized success envelope

**Given** a user requests a task they are not permitted to access through the owner flow
**When** the API evaluates the request
**Then** access is rejected according to ownership and authorization rules
**And** no unauthorized task data is returned

### Story 2.3: Cancel an Open Task

As a task poster,
I want to cancel an open task,
So that I can withdraw work that is no longer needed.

**Acceptance Criteria:**

**Given** a poster owns an open task
**When** they submit a cancel action
**Then** the task status changes to cancelled
**And** the updated task is returned using the standardized success envelope

**Given** a task is no longer in a cancellable state
**When** the poster attempts to cancel it
**Then** the API rejects the request with a business-rule error
**And** the task state remains unchanged

### Story 2.4: Discover Nearby Available Tasks

As a task performer,
I want to view a list of nearby available tasks,
So that I can find work opportunities relevant to my location.

**Acceptance Criteria:**

**Given** an authenticated performer requests available tasks with location context
**When** the discovery endpoint is called
**Then** the API returns open tasks filtered by proximity
**And** the response completes within the required performance target under normal conditions

**Given** nearby tasks are returned to a performer
**When** the task list is presented by the API
**Then** each item includes essential information such as title, distance, poster identity/trust signal, and current price
**And** the payload follows the standardized success envelope

**Given** no tasks match the discovery criteria
**When** the request is processed
**Then** the API returns an empty successful result set
**And** no error is raised for the absence of matching tasks

### Story 2.5: View Detailed Task Information Before Acceptance

As a task performer,
I want to view the full details of an available task,
So that I can decide whether to accept or negotiate it.

**Acceptance Criteria:**

**Given** a performer requests an available task detail view
**When** the task exists and is visible to them
**Then** the API returns the complete supported task detail payload
**And** it includes the fields needed to evaluate the job before taking action

**Given** a requested task does not exist or is not available to the requester
**When** the detail request is processed
**Then** the API returns the appropriate not-found or forbidden-style error
**And** the response uses the standardized error envelope

## Epic 3: Task Negotiation & Assignment

Posters and performers can agree on who will do a task and at what price, resulting in an accepted assignment.

### Story 3.1: Accept a Task at the Posted Price

As a task performer,
I want to accept an open task at the posted price,
So that I can secure the job immediately.

**Acceptance Criteria:**

**Given** an open task is available to a performer
**When** the performer accepts it at the posted price
**Then** the task is assigned according to the business rules
**And** the task status and accepted performer data are updated consistently

**Given** another performer or state change makes the task no longer open
**When** an acceptance attempt occurs
**Then** the API rejects the request with a business-rule error
**And** no conflicting assignment is created

### Story 3.2: Submit a Counter-Offer Proposal

As a task performer,
I want to propose a different price for a task,
So that I can negotiate terms before accepting the work.

**Acceptance Criteria:**

**Given** an eligible open task is available for negotiation
**When** the performer submits a valid counter-offer
**Then** the proposal is stored and linked to the task and performer
**And** the poster can later review it

**Given** the proposal payload is invalid or the task is not negotiable
**When** the request is processed
**Then** the API rejects the request appropriately
**And** no invalid proposal is created

### Story 3.3: Review and Decide on Task Proposals

As a task poster,
I want to view proposals and accept or reject them,
So that I can choose the best performer and price.

**Acceptance Criteria:**

**Given** a poster owns a task with submitted proposals
**When** they request the proposal list
**Then** the API returns the proposals associated with the task
**And** each proposal contains the data needed for decision-making

**Given** a poster accepts a valid proposal
**When** the acceptance action is processed
**Then** the performer is locked in and the task status changes to the assigned/accepted state
**And** conflicting future assignment attempts are prevented

**Given** a poster rejects a proposal
**When** the rejection is processed
**Then** the proposal state is updated accordingly
**And** the task remains available unless another valid acceptance occurs

## Epic 4: Task Communication & Execution

Once a task is accepted, both parties can communicate, track task progress, and move the task toward completion.

### Story 4.1: Send and Retrieve Task Messages

As a participant in an accepted task,
I want to send and read task-scoped messages,
So that I can coordinate task details with the other party.

**Acceptance Criteria:**

**Given** a user is one of the two participants on an accepted task
**When** they send a valid message
**Then** the message is stored chronologically under that task conversation
**And** the API returns a standardized success response

**Given** a participant requests the conversation history
**When** the request is processed
**Then** the API returns task-scoped messages in chronological order
**And** only authorized participants can access that conversation

**Given** a non-participant requests task messages
**When** authorization is evaluated
**Then** access is rejected according to task participation rules
**And** no conversation data is exposed

### Story 4.2: View Active Conversations

As a user with accepted tasks,
I want to view my active task conversations,
So that I can quickly access ongoing work discussions.

**Acceptance Criteria:**

**Given** a user participates in one or more accepted-task conversations
**When** they request their active conversations
**Then** the API returns the conversation/task list associated with that user
**And** each conversation includes enough context to identify the related task and counterpart

**Given** a user has no active conversations
**When** the request is processed
**Then** the API returns an empty successful result
**And** no error is raised

### Story 4.3: Support Near-Real-Time Message Visibility

As a task participant,
I want new messages to appear in near-real-time,
So that coordination feels responsive.

**Acceptance Criteria:**

**Given** the MVP architecture uses polling rather than WebSockets
**When** a participant requests message updates using the supported polling contract
**Then** the API returns new or changed conversation data since the prior request point
**And** the behavior supports the near-real-time requirement within the agreed architecture constraints

**Given** the polling contract is used repeatedly
**When** the endpoint is exercised under normal usage
**Then** it respects the defined rate-limiting and response-format rules
**And** it remains compatible with future task update polling patterns

### Story 4.4: Mark a Task as Completed

As a task poster,
I want to mark an accepted or in-progress task as completed,
So that the platform can move the task into settlement and rating flows.

**Acceptance Criteria:**

**Given** a poster owns a task in a completable state
**When** they mark it as completed
**Then** the task status changes to completed according to business rules
**And** the result is returned using the standardized success envelope

**Given** a task is not in a completable state or the requester lacks authority
**When** the completion request is processed
**Then** the API rejects the request appropriately
**And** the task status remains unchanged

## Epic 5: Simulated Payments & Completion

The platform can hold, release, and display simulated payments and payment history around task completion.

### Story 5.1: Hold Simulated Payment on Task Acceptance

As the platform,
I want a simulated payment hold recorded when a task is accepted,
So that the task can move through a realistic escrow-style flow.

**Acceptance Criteria:**

**Given** a task is accepted successfully
**When** the payment hold flow is triggered
**Then** a payment record is created or updated with the held state and agreed amount
**And** both the task and payment state remain consistent

**Given** the payment hold cannot be created because business or state rules are not met
**When** the hold flow is attempted
**Then** the API rejects the operation appropriately
**And** inconsistent partial settlement state is not persisted

### Story 5.2: Display Payment Status and Amount to Participants

As a task participant,
I want to see the task payment amount and settlement status,
So that I understand the current transaction state.

**Acceptance Criteria:**

**Given** a task has associated payment state
**When** an authorized participant views the task/payment details
**Then** the API returns the supported payment amount and status fields clearly
**And** unauthorized users cannot view another user's payment history or restricted payment data

### Story 5.3: Release Payment on Task Completion

As the platform,
I want simulated payment released when a task is completed,
So that the performer receives completion confirmation.

**Acceptance Criteria:**

**Given** a task has been completed and has a held payment state
**When** payment release is triggered according to the workflow
**Then** the payment state changes to released
**And** the updated settlement result is persisted consistently

**Given** a release is attempted for a task not eligible for settlement
**When** the request is processed
**Then** the API rejects the operation with a business-rule error
**And** payment state remains unchanged

### Story 5.4: View User Payment History

As a user,
I want to view my payment history,
So that I can track earnings or spending on completed tasks.

**Acceptance Criteria:**

**Given** an authenticated user requests their payment history
**When** the request is processed
**Then** the API returns only the payment records visible to that user
**And** the response uses the standardized success envelope

**Given** a user attempts to access another user's payment history
**When** authorization is evaluated
**Then** access is rejected
**And** payment data remains isolated per user

## Epic 6: Ratings, Reputation & Admin Oversight

Users can build reputation after completed work, while admins can monitor and manage platform health and interventions.

### Story 6.1: Rate the Other Party After Task Completion

As a task participant,
I want to submit a 1-5 star rating with an optional comment after completion,
So that trust can be built across the marketplace.

**Acceptance Criteria:**

**Given** a task is completed and the requester is one of the two task participants
**When** they submit a valid rating for the other party
**Then** the rating is stored with the supported score and optional comment
**And** the rating is linked to the task, rater, and rated user

**Given** a rating request violates task state, participant rules, or payload validation
**When** the request is processed
**Then** the API rejects the request appropriately
**And** no invalid rating is created

### Story 6.2: View Ratings and Reputation on User Profiles

As a platform user,
I want profile trust data to reflect ratings received,
So that I can evaluate reliability before engaging with someone.

**Acceptance Criteria:**

**Given** ratings exist for a user
**When** their public or self profile is requested through supported profile views
**Then** the returned profile includes the average rating and completed-task trust statistics
**And** users can access the list of ratings they have received where the product requires it

### Story 6.3: View Platform Dashboard Metrics

As an admin,
I want to view platform metrics and operational summaries,
So that I can monitor platform health.

**Acceptance Criteria:**

**Given** an authenticated admin requests the dashboard
**When** the request is processed
**Then** the API returns platform statistics including task totals, completion rate, registered users, and average rating or active-user metrics as supported
**And** the response uses the standardized success envelope

**Given** a non-admin requests admin dashboard data
**When** authorization is evaluated
**Then** access is rejected
**And** no admin-only metrics are exposed

### Story 6.4: View Users, Tasks, and Moderation Detail as Admin

As an admin,
I want to inspect users, tasks, and task-associated messages,
So that I can monitor platform activity and moderate issues.

**Acceptance Criteria:**

**Given** an authenticated admin requests user, task, or moderation views
**When** the request is processed
**Then** the API returns the supported administrative lists and detail views for users, tasks, and task-associated messages
**And** the data is restricted to admin-authorized access only

### Story 6.5: Manually Adjust or Release Payment as Admin

As an admin,
I want to manually intervene in payment state when needed,
So that exceptional settlement issues can be resolved.

**Acceptance Criteria:**

**Given** an authenticated admin performs a supported payment intervention
**When** the request is valid and the targeted payment exists
**Then** the payment state is updated according to the admin action
**And** the change is persisted in a way that remains consistent with task and payment history

**Given** a non-admin or invalid request attempts the same action
**When** authorization or validation is evaluated
**Then** the API rejects the request appropriately
**And** no unauthorized settlement change occurs

<!-- End story repeat -->
