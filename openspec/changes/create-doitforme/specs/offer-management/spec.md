## ADDED Requirements

### Requirement: Offer Submission
The system MUST allow runners to submit offers on OPEN tasks.

#### Scenario: Runner makes an offer
- **WHEN** a runner submits an offer with a proposed price and message on an OPEN task
- **THEN** the system creates an Offer with status PENDING

### Requirement: Offer Acceptance
The system MUST allow the task creator to accept an offer, updating task state.

#### Scenario: Creator accepts an offer
- **WHEN** the task creator accepts a PENDING offer
- **THEN** the Offer status becomes ACCEPTED, the Task status becomes ASSIGNED, and the Task runner_id is updated to the Offer runner_id

### Requirement: Self-Offer Restriction
The system MUST prevent users from making offers on their own tasks.

#### Scenario: Creator makes an offer
- **WHEN** the task creator tries to make an offer on their own task
- **THEN** the system rejects the offer creation

### Requirement: Self-Acceptance Restriction
The system MUST prevent users from accepting their own tasks. (Note: Covered by Self-Offer Restriction).

#### Scenario: Creator accepts own task
- **WHEN** a user tries to accept a task where they are the creator
- **THEN** the system rejects it
