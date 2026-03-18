---
title: DoItForMe REST API Contract
version: 1.0
date: 2026-03-18
status: Draft
---

# DoItForMe REST API Contract

**Backend Framework:** Python (Flask/FastAPI)
**Database:** PostgreSQL
**Real-time Strategy:** Polling
**Authentication:** JWT Tokens

---

## 1. API Overview

### Base URL
```
http://localhost:5000/api/v1
```

### Response Format
All responses are JSON. Every response includes a status and data/error:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2026-03-18T10:30:00Z"
}
```

Error response:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { ... }
  },
  "timestamp": "2026-03-18T10:30:00Z"
}
```

---

## 2. Authentication & Authorization

### JWT Token Structure

**Request Header:**
```
Authorization: Bearer <jwt_token>
```

**Token Payload:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "poster|performer|admin",
  "iat": 1710754200,
  "exp": 1711359000
}
```

**Token Expiration:** 7 days

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!",
  "name": "John Doe",
  "role": "poster|performer"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "userId": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "poster",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_EMAIL",
    "message": "Email already exists"
  }
}
```

---

#### POST /auth/login
Authenticate user and return JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "userId": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "poster",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

---

#### POST /auth/logout
Invalidate current session/token.

**Request Header:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}
```

---

## 3. User Management Endpoints

#### GET /users/:userId
Retrieve user profile with stats.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "userId": "user_123",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "poster|performer",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "city": "New York"
    },
    "rating": 4.8,
    "completedTasks": 12,
    "ratingCount": 15,
    "joinedDate": "2026-01-15T00:00:00Z"
  }
}
```

---

#### PUT /users/:userId
Update user profile information.

**Request:**
```json
{
  "name": "John Updated",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "userId": "user_123",
    "name": "John Updated",
    "location": { ... }
  }
}
```

---

#### POST /auth/logout
Invalidate user session.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}
```

---

## 4. Task Management Endpoints

#### POST /tasks
Create a new task.

**Request:**
```json
{
  "title": "Pick up dry cleaning",
  "description": "Get my suit from Green Dry Cleaners on 5th Ave",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "price": 15.00,
  "category": "errand"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "taskId": "task_456",
    "title": "Pick up dry cleaning",
    "description": "...",
    "location": { ... },
    "price": 15.00,
    "status": "open",
    "createdBy": "user_123",
    "createdAt": "2026-03-18T10:00:00Z",
    "proposals": []
  }
}
```

---

#### GET /tasks
List available tasks filtered by location.

**Query Parameters:**
- `latitude` (required): User's latitude
- `longitude` (required): User's longitude
- `radius` (optional): Search radius in km (default: 5)
- `category` (optional): Filter by category
- `status` (optional): open, in-progress, completed, cancelled

**Request:**
```
GET /tasks?latitude=40.7128&longitude=-74.0060&radius=5&status=open
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "taskId": "task_456",
        "title": "Pick up dry cleaning",
        "description": "Get my suit from Green Dry Cleaners",
        "location": { ... },
        "distance": 0.5,
        "price": 15.00,
        "status": "open",
        "postedBy": "Maria",
        "posterRating": 4.8,
        "createdAt": "2026-03-18T10:00:00Z",
        "proposalCount": 2
      }
    ],
    "totalCount": 10,
    "pageNumber": 1,
    "pageSize": 20
  }
}
```

---

#### GET /tasks/:taskId
Get task details.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "taskId": "task_456",
    "title": "Pick up dry cleaning",
    "description": "...",
    "location": { ... },
    "price": 15.00,
    "status": "open",
    "createdBy": {
      "userId": "user_123",
      "name": "Maria",
      "rating": 4.8
    },
    "acceptedBy": null,
    "proposals": [
      {
        "proposalId": "prop_789",
        "performerId": "user_456",
        "performerName": "Alex",
        "performerRating": 4.9,
        "proposedPrice": 15.00,
        "status": "pending",
        "createdAt": "2026-03-18T10:05:00Z"
      }
    ],
    "createdAt": "2026-03-18T10:00:00Z"
  }
}
```

---

#### POST /tasks/:taskId/accept
Accept a task at posted price (creates proposal with instant acceptance).

**Request:**
```json
{
  "proposedPrice": 15.00
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "taskId": "task_456",
    "status": "accepted",
    "acceptedBy": "user_456",
    "acceptedPrice": 15.00,
    "acceptedAt": "2026-03-18T10:10:00Z",
    "paymentId": "pay_999"
  }
}
```

---

#### POST /tasks/:taskId/propose
Propose a different price for a task.

**Request:**
```json
{
  "proposedPrice": 12.00
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "proposalId": "prop_789",
    "taskId": "task_456",
    "performerId": "user_456",
    "proposedPrice": 12.00,
    "status": "pending",
    "createdAt": "2026-03-18T10:05:00Z"
  }
}
```

---

#### POST /tasks/:taskId/proposals/:proposalId/accept
Task poster accepts a performer's price proposal.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "taskId": "task_456",
    "status": "accepted",
    "acceptedBy": "user_456",
    "acceptedPrice": 12.00,
    "paymentId": "pay_999"
  }
}
```

---

#### POST /tasks/:taskId/proposals/:proposalId/reject
Task poster rejects a performer's proposal.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "proposalId": "prop_789",
    "status": "rejected"
  }
}
```

---

#### PUT /tasks/:taskId/status
Update task status (in-progress, completed, cancelled).

**Request:**
```json
{
  "status": "completed"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "taskId": "task_456",
    "status": "completed",
    "completedAt": "2026-03-18T11:30:00Z"
  }
}
```

---

#### GET /users/:userId/tasks
Get all tasks posted by or accepted by a user.

**Query Parameters:**
- `role` (optional): `posted` or `accepted` (default: all)
- `status` (optional): Filter by status

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tasks": [ ... ],
    "totalCount": 5
  }
}
```

---

## 5. Chat/Messaging Endpoints

#### POST /tasks/:taskId/messages
Send a message in a task conversation.

**Request:**
```json
{
  "text": "Hi! I'm on my way to the dry cleaner. Should be there in 10 minutes."
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "messageId": "msg_001",
    "taskId": "task_456",
    "senderId": "user_456",
    "senderName": "Alex",
    "text": "Hi! I'm on my way...",
    "createdAt": "2026-03-18T10:15:00Z",
    "readBy": [ "user_456" ]
  }
}
```

---

#### GET /tasks/:taskId/messages
Get all messages for a task conversation.

**Query Parameters:**
- `limit` (optional): Number of messages (default: 50)
- `offset` (optional): Pagination offset

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "messageId": "msg_001",
        "senderId": "user_456",
        "senderName": "Alex",
        "text": "On my way...",
        "createdAt": "2026-03-18T10:15:00Z",
        "readBy": [ "user_123", "user_456" ]
      }
    ],
    "totalCount": 8
  }
}
```

---

#### GET /users/:userId/conversations
Get all active conversations for a user (tasks with messages).

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "taskId": "task_456",
        "taskTitle": "Pick up dry cleaning",
        "otherUserId": "user_456",
        "otherUserName": "Alex",
        "lastMessage": "On my way...",
        "lastMessageTime": "2026-03-18T10:15:00Z",
        "unreadCount": 0
      }
    ],
    "totalCount": 3
  }
}
```

---

## 6. Payment Endpoints (Simulated)

#### POST /tasks/:taskId/payment/hold
Hold payment in escrow when task is accepted.

**Request:**
```json
{
  "amount": 15.00,
  "currency": "USD"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "paymentId": "pay_999",
    "taskId": "task_456",
    "amount": 15.00,
    "currency": "USD",
    "status": "held",
    "postedBy": "user_123",
    "performedBy": "user_456",
    "createdAt": "2026-03-18T10:10:00Z"
  }
}
```

---

#### POST /tasks/:taskId/payment/release
Release payment to performer when task is completed.

**Request:**
```json
{}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "paymentId": "pay_999",
    "status": "released",
    "releasedAt": "2026-03-18T11:35:00Z",
    "performerAccountCredit": 15.00
  }
}
```

---

#### GET /users/:userId/payments
Get payment history (earnings for performers, expenses for posters).

**Query Parameters:**
- `type` (optional): `earned` or `spent`
- `status` (optional): `held`, `released`, `cancelled`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "paymentId": "pay_999",
        "taskId": "task_456",
        "taskTitle": "Pick up dry cleaning",
        "amount": 15.00,
        "type": "earned|spent",
        "status": "released",
        "otherUserName": "Maria",
        "createdAt": "2026-03-18T10:10:00Z",
        "releasedAt": "2026-03-18T11:35:00Z"
      }
    ],
    "totalEarned": 125.50,
    "totalSpent": 45.00
  }
}
```

---

## 7. Ratings Endpoints

#### POST /tasks/:taskId/rating
Rate a user after task completion.

**Request:**
```json
{
  "rating": 5,
  "comment": "Great job! Very professional and quick."
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "ratingId": "rating_001",
    "taskId": "task_456",
    "ratedBy": "user_123",
    "ratedUser": "user_456",
    "rating": 5,
    "comment": "Great job!...",
    "createdAt": "2026-03-18T11:40:00Z"
  }
}
```

---

#### GET /users/:userId/ratings
Get all ratings received by a user.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "ratings": [
      {
        "ratingId": "rating_001",
        "ratedBy": "Maria",
        "taskId": "task_456",
        "taskTitle": "Pick up dry cleaning",
        "rating": 5,
        "comment": "Great job!...",
        "createdAt": "2026-03-18T11:40:00Z"
      }
    ],
    "totalCount": 12,
    "averageRating": 4.8,
    "ratingDistribution": {
      "5": 10,
      "4": 2,
      "3": 0,
      "2": 0,
      "1": 0
    }
  }
}
```

---

## 8. Admin Endpoints

#### GET /admin/dashboard
Get platform metrics and statistics.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "metrics": {
      "totalUsers": 47,
      "totalTasks": 156,
      "completedTasks": 125,
      "completionRate": 0.801,
      "activeUsers": 23,
      "averageRating": 4.5,
      "tasksPostedToday": 8,
      "tasksCompletedToday": 5
    }
  }
}
```

---

#### GET /admin/users
Get list of all users.

**Query Parameters:**
- `limit` (optional): Page size (default: 20)
- `offset` (optional): Pagination offset
- `role` (optional): Filter by role

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "userId": "user_123",
        "name": "Maria",
        "email": "maria@example.com",
        "role": "poster|performer",
        "rating": 4.8,
        "completedTasks": 12,
        "joinedAt": "2026-01-15T00:00:00Z",
        "lastActiveAt": "2026-03-18T10:30:00Z"
      }
    ],
    "totalCount": 47
  }
}
```

---

#### GET /admin/tasks
Get list of all tasks.

**Query Parameters:**
- `status` (optional): Filter by status
- `limit` (optional): Page size (default: 20)
- `offset` (optional): Pagination offset

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "taskId": "task_456",
        "title": "Pick up dry cleaning",
        "postedBy": "Maria",
        "status": "completed",
        "price": 15.00,
        "completedBy": "Alex",
        "createdAt": "2026-03-18T10:00:00Z",
        "completedAt": "2026-03-18T11:35:00Z"
      }
    ],
    "totalCount": 156
  }
}
```

---

#### PUT /admin/payments/:paymentId/release
Manually release a held payment.

**Request:**
```json
{
  "reason": "Manual override by admin"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "paymentId": "pay_999",
    "status": "released",
    "releasedAt": "2026-03-18T12:00:00Z",
    "releasedBy": "admin_001"
  }
}
```

---

## 9. Error Handling

### Standard HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate email, invalid state |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Unexpected server error |

### Error Response Format

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "Additional context"
    }
  },
  "timestamp": "2026-03-18T10:30:00Z"
}
```

### Common Error Codes

- `INVALID_INPUT` - Validation failed
- `INVALID_EMAIL` - Email format invalid or already exists
- `INVALID_PASSWORD` - Password doesn't meet requirements
- `INVALID_CREDENTIALS` - Email/password mismatch
- `UNAUTHORIZED` - Missing/invalid JWT token
- `FORBIDDEN` - User doesn't have permission
- `NOT_FOUND` - Resource not found
- `TASK_NOT_OPEN` - Cannot accept closed task
- `INVALID_STATE_TRANSITION` - Invalid status change
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## 10. Rate Limiting

**Global Limits:**
- Authenticated users: 100 requests/minute
- Unauthenticated: 20 requests/minute

**Specific Limits:**
- Task creation: 20 tasks/day per user
- Message sending: 50 messages/minute per task
- Rating: 1 rating per completed task

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1710754200
```

---

## 11. Security Requirements

### Headers Required
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character (!@#$%^&*)

### Data Validation
- Email: Valid format (RFC 5322)
- Location: Valid lat/long coordinates
- Price: Positive number, max 2 decimal places
- Rating: Integer 1-5
- Message: Non-empty, max 1000 characters

---

## 12. Database Schema (Quick Reference)

### Tables
- `users` - User accounts
- `tasks` - Posted tasks
- `proposals` - Price proposals
- `messages` - Chat messages
- `payments` - Payment ledger
- `ratings` - User ratings

**See separate Database Schema document for full details.**

---

**API Contract Version:** 1.0
**Last Updated:** 2026-03-18
**Status:** Ready for implementation
