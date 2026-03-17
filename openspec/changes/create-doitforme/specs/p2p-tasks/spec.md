## ADDED Requirements

### Requirement: Task Creation
The system MUST allow authenticated users to create P2P tasks.

#### Scenario: Valid Task Creation
- **WHEN** a user submits task details (title, description, category, precio_inicial, location)
- **THEN** the system creates a Task with status OPEN and creator_id set to the user's ID

### Requirement: Task State Transitions
The system MUST enforce strict state transitions for tasks (OPEN -> ASSIGNED -> COMPLETED or CANCELLED).

#### Scenario: Invalid State Transition
- **WHEN** a user tries to complete an OPEN task
- **THEN** the system rejects the request
