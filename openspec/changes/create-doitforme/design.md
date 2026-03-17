## Context
DoItForMe is a new P2P service platform connecting users needing errands (creators) with users willing to do them (runners). We need a base backend architecture using Node.js, Express, PostgreSQL, and Prisma to handle Users, Tasks, and Offers.

## Goals / Non-Goals

**Goals:**
- Provide a scalable REST API for user, task, and offer management.
- Ensure data integrity with PostgreSQL and Prisma.
- Secure endpoints with basic JWT authentication.
- Implement strict business logic for offer acceptance.

**Non-Goals:**
- Payment processing (out of scope for MVP).
- Real-time notifications or WebSockets (can be added later).

## Decisions
- **Stack:** Node.js + Express + Prisma + PostgreSQL.
  - *Rationale*: High developer velocity, excellent type safety with Prisma, and robust relational data modeling.
- **Authentication:** JWT (JSON Web Tokens).
  - *Rationale*: Stateless, easy to integrate with mobile/web clients.
- **Offer Acceptance Logic:** PATCH endpoint on `/api/offers/:id/accept` which uses a transaction to update Offer status to `ACCEPTED`, other offers to `REJECTED`, Task status to `ASSIGNED`, and `runner_id` on the Task.
  - *Rationale*: Transaction ensures consistency.

## Risks / Trade-offs
- [Risk] Unauthorized offer acceptance → Mitigation: API must verify the requester is the `creator_id` of the associated task.
- [Risk] Creator accepting their own offer → Mitigation: Validation rule preventing creator from being the runner.
