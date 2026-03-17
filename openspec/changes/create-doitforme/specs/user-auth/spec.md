## ADDED Requirements

### Requirement: User Registration
The system MUST allow users to register with name, email, and password.

#### Scenario: Successful Registration
- **WHEN** a user submits valid registration details
- **THEN** the system creates a new User with id, name, email, rating=0, and is_runner=false

### Requirement: User Authentication
The system MUST authenticate users via email and password.

#### Scenario: Successful Login
- **WHEN** a user logs in with correct credentials
- **THEN** the system returns a JWT token
