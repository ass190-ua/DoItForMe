## Why
The goal is to build the backend for "DoItForMe", a P2P service platform where users can post tasks (errands, shopping, pickup) and "Runners" can make offers to complete them. This change sets up the foundational database schema, API endpoints, and authentication mechanism from scratch.

## What Changes
- Set up a PostgreSQL database.
- Create database schema with `Users`, `Tasks`, and `Offers`.
- Implement REST API endpoints for user registration, task creation, and offer management.
- Implement critical business logic for state transitions: when an offer is accepted (via PATCH), the task status changes automatically to `ASSIGNED` and the `runner_id` is updated.
- Implement validation rules: users cannot accept offers on their own tasks.
- Add basic authentication mechanism to secure the endpoints.

## Capabilities

### New Capabilities
- `p2p-tasks`: Core system for users to create and manage P2P tasks.
- `offer-management`: System allowing runners to bid on tasks and creators to accept them.
- `user-auth`: Basic registration and authentication for users.

### Modified Capabilities

## Impact
- New database schema requires migration.
- New API routes added to the application.
- Introduction of basic authentication middleware for protected routes.
