---
stepsCompleted: ["step-01-init", "step-02-discovery", "step-02b-vision", "step-02c-executive-summary", "step-03-success", "step-04-journeys", "step-05-domain", "step-06-innovation", "step-07-project-type", "step-08-scoping", "step-09-functional", "step-10-nonfunctional", "step-11-polish"]
inputDocuments: ["user-provided specification (DoItForMe platform)"]
workflowType: 'prd'
projectName: 'DoItForMe'
date: '2026-03-18'
classification:
  projectType: 'api_backend'
  domain: 'fintech'
  complexity: 'high'
  projectContext: 'greenfield'
  focusAreas:
    - Task management APIs
    - Payment processing
    - User authentication & ratings
    - Real-time updates & chat
---

# Product Requirements Document - DoItForMe

**Author:** Liu
**Date:** 2026-03-18

## Executive Summary

DoItForMe is a hyper-local P2P marketplace that enables users to instantly monetize spare time by helping neighbors with everyday tasks. The platform connects task posters (who need help) with task performers (who want immediate income) within their local community. **For this study project, payment processing is simulated** — the backend manages transactions conceptually without actual payment integration.

**Target Users:**
- Task Posters: Busy professionals, students, and individuals lacking time for daily errands (waiting in lines, shopping, package pickup, service errands)
- Task Performers: Anyone with spare time seeking immediate, flexible income without formal employment

**Core Problem Solved:**
People have untapped economic value in their spare time. Simultaneously, their neighbors have repetitive, low-skill tasks they don't have time for. This platform demonstrates the frictionless marketplace model through simulated transactions.

### What Makes This Special

**Market Differentiation:**
Unlike specialized delivery platforms (food, packages), DoItForMe is task-agnostic—enabling any legal task delegation. This generalist approach creates a flexible, high-volume marketplace model.

**Core Innovation:**
Direct P2P connection + transparent dynamic pricing (negotiation/bidding) + community trust system (ratings/reviews) = instant local economy with zero credentialing barriers.

## Project Classification

- **Project Type:** API Backend
- **Domain:** Gig Economy Marketplace
- **Complexity:** Medium (simulated payments, real-time coordination, trust/rating system)
- **Project Context:** Greenfield (new study project)

## Success Criteria

### User Success

**Task Posters:**
- Post a task in under 2 minutes (simple form with location, description, initial price)
- Receive first proposal within 5 minutes
- Successfully negotiate price and execute task handoff
- Complete task and release payment
- **"Aha moment":** When they see someone accept their task proposal in real-time

**Task Performers:**
- Find nearby tasks within 1 minute of opening the app
- Accept a task and start earning the same day
- Complete task and receive payment confirmation
- Build reputation through ratings and reviews
- **"Aha moment":** When they complete their first task and see payment released + positive rating

### Business Success (Study Demo)

- **User Adoption:** 50+ registered users (mix of posters and performers)
- **Task Completion Rate:** 80%+ of posted tasks successfully completed or negotiated
- **Platform Engagement:** Average 10+ tasks posted per day in test period
- **User Retention:** 60%+ of users return for second transaction
- **Trust Signal:** Average rating 4.5+ stars (builds confidence in P2P model)

### Technical Success

- **Real-time Performance:** Task listings update within 2 seconds of posting
- **Chat Reliability:** Messages delivered within 500ms
- **Geolocation Accuracy:** Location services function within city-block precision
- **Payment Simulation:** Transactions recorded and retrievable (no actual payment processing)
- **User Authentication:** Secure login/signup with persistent sessions
- **Data Persistence:** All tasks, user ratings, and transactions persist correctly

### Measurable Outcomes

- Tasks posted: Count
- Tasks completed: Count + percentage of total
- Average negotiation time: Minutes from post to acceptance
- User ratings distribution: 4-5 stars, 3-4 stars, <3 stars
- Chat message volume: Messages per task
- Daily active users: Returning users percentage
- Session duration: Average time in app per session

## Product Scope

### MVP - Minimum Viable Product

**Essential to prove the concept:**
- User authentication (signup/login)
- Task creation (post task with location, description, price)
- Task discovery (list nearby tasks, filter by category)
- Task negotiation (accept task or propose counter-price)
- Chat system (task-level messaging between poster and performer)
- Simulated payment (accept payment, hold funds, release on completion)
- Basic ratings (1-5 stars + comment after task completion)

### Growth Features (Post-MVP)

- Task categorization and search filters
- User profiles with portfolio/history
- Advanced rating analytics (response time, completion rate)
- Notification system (price proposals, task acceptance, completion reminders)
- Task history and repeat user matching
- Payment analytics dashboard
- Dispute/cancellation workflow

### Vision (Future)

- Subscription tiers (free vs. premium performer benefits)
- Task insurance/guarantee system
- Community reputation badges
- Referral program
- Scheduled/recurring tasks
- Team tasks (multiple performers on one task)
- Task reviews and testimonials

## User Journeys

### Journey 1: Task Poster (Happy Path)

**María posts a task:**
1. Opens app → Taps "Post Task"
2. Fills form: description, location, price ($15)
3. Submits task
4. Sees proposal from Alex (willing to do it for $15)
5. Accepts proposal
6. Alex completes task and marks done
7. María releases payment to Alex
8. María rates Alex 5★

**Reveals:** Task creation, task acceptance, payment release, ratings

### Journey 2: Task Performer (Happy Path)

**Alex finds and completes a task:**
1. Opens app → Sees nearby tasks in list
2. Finds María's task ($15)
3. Taps "Accept Task"
4. Chat with María about details if needed
5. Completes task, marks "Done"
6. Gets payment ($15) released
7. Gets 5★ rating from María

**Reveals:** Task discovery, task acceptance, task completion, payment receipt, ratings

### Journey 3: Admin - Monitor Platform

**Admin checks platform health:**
1. Views dashboard: total tasks, completed tasks, active users
2. Can view task list and user profiles
3. Can manually adjust payment if needed

**Reveals:** Admin dashboard, platform metrics

### Journey Requirements Summary

**Core backend capabilities needed:**
- Task CRUD (create, list, accept, mark complete)
- User authentication
- Real-time task updates
- Chat/messaging between task pairs
- Simulated payment (hold, release)
- Rating system
- User profiles with stats
- Geolocation and task filtering
- Admin dashboard with basic metrics

## API Backend Specific Requirements

### API Architecture Overview

**REST API** with JSON request/response format. Endpoints organized by resource.

### Core Endpoints

**Authentication:**
- `POST /auth/register` - Create new user account
- `POST /auth/login` - User login (returns JWT token)
- `POST /auth/logout` - User logout

**Tasks:**
- `POST /tasks` - Create new task
- `GET /tasks` - List nearby tasks (filtered by location)
- `GET /tasks/:id` - Get task details
- `POST /tasks/:id/accept` - Accept a task
- `PUT /tasks/:id/status` - Update task status (in-progress, completed, cancelled)

**Chat:**
- `POST /tasks/:id/messages` - Send message for a task
- `GET /tasks/:id/messages` - Get chat history for a task

**Payments (Simulated):**
- `POST /tasks/:id/payment/hold` - Hold payment from task poster
- `POST /tasks/:id/payment/release` - Release payment to performer

**Ratings:**
- `POST /tasks/:id/rating` - Rate task performer or poster

**User Profiles:**
- `GET /users/:id` - Get user profile
- `PUT /users/:id` - Update user profile
- `GET /users/:id/history` - Get user's task history

**Admin:**
- `GET /admin/dashboard` - Platform metrics (task count, completion rate, active users)

### Authentication & Authorization

- **JWT Tokens** for stateless authentication
- Token includes user ID and role (poster, performer, admin)
- Token expiration: 7 days
- Refresh endpoint to extend session

### Data Formats

**Core JSON structures:**
- Task: `{id, title, description, location, price, status, createdBy, acceptedBy, createdAt}`
- User: `{id, name, email, role, location, rating, completedTasks}`
- Message: `{id, taskId, senderID, text, timestamp}`
- Payment: `{id, taskId, amount, status, createdAt}`
- Rating: `{id, taskId, ratedBy, ratedUser, score, comment}`

### Error Responses

Standard HTTP status codes:
- 400 - Bad request (invalid data)
- 401 - Unauthorized (no token)
- 403 - Forbidden (no permission)
- 404 - Not found
- 429 - Rate limit exceeded
- 500 - Server error

### Rate Limiting

- Authenticated users: 100 requests/minute
- Task creation limit: 20 tasks/day per user
- Message limit: 50 messages/minute

### API Documentation

- OpenAPI/Swagger specification
- Auto-generated interactive API docs endpoint: `GET /docs`

### Implementation Considerations

- Stateless design (easy to scale horizontally)
- Database: Store tasks, users, messages, payments, ratings
- Real-time updates: WebSockets for live task notifications and chat
- Geolocation: Accept lat/long coordinates, calculate distance server-side

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**Approach:** Lean MVP - Prove the core P2P marketplace concept works with essential features only.

**Core Value Delivery:** Task posters find help, performers find work, transactions complete reliably.

**Team Size:** 2-3 developers + 1 project lead (for a study demo)

### Phase 1: MVP (Launch-Ready)

**Must-Have Features:**
- User authentication (signup/login with JWT)
- Task CRUD (create, list, filter by location, accept)
- Task negotiation (accept or counter-propose price)
- Chat system (task-level messaging)
- Simulated payment (hold funds, release on completion)
- Basic 1-5 star ratings with comments
- User profiles with completion stats
- Geolocation filtering (find nearby tasks)
- Admin dashboard (task metrics, user list, manual payment override)

**Success Metrics:** 50+ users, 80%+ completion rate, 4.5+ avg rating

### Phase 2: Growth Features (Post-MVP)

- Task categorization & advanced filtering
- User reputation badges (Rising Star, Trusted Performer)
- Notification system (price proposals, task updates, reminders)
- Task history & repeat user suggestions
- Payment analytics dashboard
- Dispute/cancellation workflow
- User reviews & portfolio building

### Phase 3: Expansion (Vision)

- Subscription tiers (premium features for performers)
- Insurance/guarantee system
- Referral program
- Scheduled/recurring tasks
- Team tasks (multiple performers)
- In-app task reviews & testimonials

### Risk Mitigation

**Technical Risks:**
- Real-time chat via WebSockets could be complex → Start with polling, upgrade to WebSockets if needed
- Geolocation precision → Use simple lat/long with distance calculation, no complex routing

**Market Risks:**
- Cold start (few users/tasks) → Bootstrap with test data, recruit beta testers early
- Trust issues → Strong rating system in MVP + easy dispute process

**Resource Risks:**
- If smaller team → Drop dispute workflow from MVP, handle manually initially
- If time-constrained → Use existing chat library, don't build from scratch

## Functional Requirements

### User Management

- FR1: A new user can register with email and password
- FR2: A registered user can log in with email and password
- FR3: A logged-in user can view their profile (name, rating, completed tasks count)
- FR4: A user can update their profile information
- FR5: A user can view another user's profile with their stats and ratings
- FR6: A user can log out and invalidate their session

### Task Creation & Management

- FR7: A task poster can create a new task with title, description, location, and initial price offer
- FR8: A task poster can view all their posted tasks
- FR9: A task poster can view details of a specific task
- FR10: A task can display its current status (open, in-progress, completed, cancelled)
- FR11: A task poster can cancel an open task
- FR12: A task poster can mark a task as completed (triggering payment release)

### Task Discovery & Filtering

- FR13: A task performer can view a list of available tasks
- FR14: Tasks are filtered by proximity to the performer's location (distance-based)
- FR15: Tasks display essential information: title, location distance, posted by, current price
- FR16: A performer can view detailed information about a task before accepting

### Task Negotiation

- FR17: A task performer can accept a task at the posted price
- FR18: A task performer can propose a different price instead of accepting the posted price
- FR19: A task poster can view proposals/counter-offers on their task
- FR20: A task poster can accept or reject a performer's counter-offer
- FR21: Once a proposal is accepted, the task status changes to "accepted" and the performer is locked in

### Communication

- FR22: Two users on an accepted task can send messages to each other
- FR23: Message history is visible chronologically within a task
- FR24: Users can view all active conversations (tasks with accepted performers)
- FR25: Messages appear in real-time or near-real-time for both parties

### Payment Simulation

- FR26: When a task is accepted, payment is held in a simulated escrow
- FR27: The payment amount is displayed clearly to both parties
- FR28: When a task is marked complete, payment is released to the performer
- FR29: A user can view their payment history (earnings or spent)
- FR30: Admin can manually release or hold payment if needed

### Ratings & Reputation

- FR31: After a task is completed, the task poster can rate the performer (1-5 stars with optional comment)
- FR32: After a task is completed, the performer can rate the task poster (1-5 stars with optional comment)
- FR33: A user's profile displays their average rating across all completed tasks
- FR34: A user can view all ratings they've received

### Admin Dashboard

- FR35: Admin can view total number of tasks posted
- FR36: Admin can view number of completed tasks and completion rate
- FR37: Admin can view total number of registered users
- FR38: Admin can view a list of all users
- FR39: Admin can view a list of all tasks with their statuses
- FR40: Admin can view task details and associated messages (for moderation)
- FR41: Admin can manually adjust or release a payment
- FR42: Admin can view platform statistics (completion rate, avg rating, active users)

## Non-Functional Requirements

### Performance

- NFR1: Task listings load within 2 seconds
- NFR2: Chat messages display within 1 second of sending
- NFR3: Location-based task filtering completes within 2 seconds
- NFR4: User authentication (login/signup) completes within 3 seconds
- NFR5: The system supports at least 50 concurrent users without degradation

### Security

- NFR6: All user passwords are hashed and never stored in plain text
- NFR7: All API requests require valid JWT authentication token
- NFR8: User can only view/modify their own tasks and payments
- NFR9: Admin endpoints are restricted and cannot be accessed by regular users
- NFR10: Chat messages are not visible to users not involved in the task
- NFR11: Payment data is isolated per user (users cannot view others' payment history)
- NFR12: All sensitive API communications use HTTPS/SSL encryption

### Scalability

- NFR13: System architecture supports horizontal scaling (multiple backend instances)
- NFR14: Database queries are optimized to handle 10,000+ tasks
- NFR15: Real-time messaging can handle 100+ concurrent chat sessions
- NFR16: Location-based queries are indexed for fast response times

