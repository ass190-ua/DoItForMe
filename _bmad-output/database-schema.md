---
title: DoItForMe PostgreSQL Database Schema
version: 1.0
date: 2026-03-18
status: Ready for Implementation
---

# DoItForMe PostgreSQL Database Schema

**Database:** PostgreSQL
**Purpose:** Backend storage for P2P task marketplace
**Timezone:** UTC (all timestamps)

---

## 1. Entity Relationship Diagram

```
┌─────────────────────┐
│       USERS         │
├─────────────────────┤
│ user_id (PK)        │
│ email (UNIQUE)      │
│ password_hash       │
│ name                │
│ role                │
│ latitude            │
│ longitude           │
│ rating              │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
     ┌─────┴─────┬──────────┬──────────┬──────────┐
     │           │          │          │          │
     ▼           ▼          ▼          ▼          ▼
  TASKS     PROPOSALS   MESSAGES   PAYMENTS   RATINGS
  (posted)  (proposals) (chat)     (ledger)   (reviews)
  (accepted)
```

---

## 2. Tables Definition

### 2.1 USERS Table

Stores user accounts and profiles.

```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(100) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('poster', 'performer', 'admin')),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  rating DECIMAL(3, 2) DEFAULT 5.00 CHECK (rating >= 0 AND rating <= 5),
  completed_tasks_count INTEGER DEFAULT 0,
  rating_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_location ON users(latitude, longitude);
CREATE INDEX idx_users_rating ON users(rating);
```

**Columns:**
- `user_id` - Unique user identifier (UUID)
- `email` - User email (unique, used for login)
- `password_hash` - Bcrypt hashed password
- `name` - User's display name
- `role` - Account type: `poster`, `performer`, or `admin`
- `latitude/longitude` - Last known user location
- `rating` - Average rating (0-5, calculated from ratings table)
- `completed_tasks_count` - Cache of completed tasks
- `rating_count` - Total number of ratings received
- `created_at/updated_at` - Timestamps

---

### 2.2 TASKS Table

Stores task postings.

```sql
CREATE TABLE tasks (
  task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  created_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  accepted_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'open'
    CHECK (status IN ('open', 'accepted', 'in_progress', 'completed', 'cancelled')),
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  category VARCHAR(50),
  initial_price DECIMAL(10, 2) NOT NULL CHECK (initial_price > 0),
  accepted_price DECIMAL(10, 2),
  completion_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_accepted_by ON tasks(accepted_by);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_location ON tasks(latitude, longitude);
CREATE INDEX idx_tasks_category ON tasks(category);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**Columns:**
- `task_id` - Unique task identifier (UUID)
- `title` - Task title (e.g., "Pick up dry cleaning")
- `description` - Detailed task description
- `created_by` - User who posted the task (FK to users)
- `accepted_by` - User who accepted the task (FK to users)
- `status` - Task lifecycle state
- `latitude/longitude` - Task location
- `category` - Task category (errand, shopping, waiting, etc.)
- `initial_price` - Original price offered
- `accepted_price` - Final negotiated price
- `completion_date` - When task was marked complete
- `created_at/updated_at` - Timestamps

**Status Transitions:**
```
open → accepted → in_progress → completed
open → accepted → completed (can skip in_progress)
open → cancelled (anytime)
accepted → cancelled (with permission)
```

---

### 2.3 PROPOSALS Table

Stores price proposals when performer suggests different price.

```sql
CREATE TABLE proposals (
  proposal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  performer_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  proposed_price DECIMAL(10, 2) NOT NULL CHECK (proposed_price > 0),
  status VARCHAR(20) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'accepted', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_proposals_task_id ON proposals(task_id);
CREATE INDEX idx_proposals_performer_id ON proposals(performer_id);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_created_at ON proposals(created_at);
```

**Columns:**
- `proposal_id` - Unique proposal identifier
- `task_id` - Reference to task (FK)
- `performer_id` - User making proposal (FK)
- `proposed_price` - Counter-offer price
- `status` - Proposal state (pending, accepted, rejected)
- `created_at/updated_at` - Timestamps

**Notes:**
- When performer accepts at posted price: create with status='accepted'
- When performer counter-offers: create with status='pending'
- Task poster approves by updating status to 'accepted'

---

### 2.4 MESSAGES Table

Stores chat messages between users on a task.

```sql
CREATE TABLE messages (
  message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  recipient_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  text TEXT NOT NULL CHECK (length(text) > 0 AND length(text) <= 1000),
  read_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_task_id ON messages(task_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_recipient_id ON messages(recipient_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_read_at ON messages(read_at) WHERE read_at IS NULL;
```

**Columns:**
- `message_id` - Unique message identifier
- `task_id` - Reference to task conversation (FK)
- `sender_id` - Who sent the message (FK)
- `recipient_id` - Who receives the message (FK)
- `text` - Message content (1-1000 characters)
- `read_at` - When recipient read message (NULL = unread)
- `created_at` - Message timestamp

**Notes:**
- Only task poster and accepted performer can message each other
- Enforce in application logic, not database
- Use polling: client polls GET /tasks/:taskId/messages?since=<timestamp>

---

### 2.5 PAYMENTS Table

Stores payment ledger (simulated transactions).

```sql
CREATE TABLE payments (
  payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  poster_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  performer_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) NOT NULL DEFAULT 'held'
    CHECK (status IN ('held', 'released', 'refunded', 'cancelled')),
  held_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  released_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_payments_task_id ON payments(task_id);
CREATE INDEX idx_payments_poster_id ON payments(poster_id);
CREATE INDEX idx_payments_performer_id ON payments(performer_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);
```

**Columns:**
- `payment_id` - Unique payment identifier
- `task_id` - Reference to task (FK)
- `poster_id` - Task poster (payer) (FK)
- `performer_id` - Task performer (payee) (FK)
- `amount` - Payment amount
- `currency` - Currency code (USD, EUR, etc.)
- `status` - Payment state (held, released, refunded, cancelled)
- `held_at` - When payment was held
- `released_at` - When payment was released to performer
- `created_at/updated_at` - Timestamps

**Payment Flow:**
```
1. Task accepted → payment status='held'
2. Task completed → payment status='released' + released_at=NOW()
3. Dispute → status='refunded' or admin override
```

---

### 2.6 RATINGS Table

Stores user ratings and reviews.

```sql
CREATE TABLE ratings (
  rating_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  rated_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  rated_user UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
  comment TEXT CHECK (length(comment) <= 500),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ratings_task_id ON ratings(task_id);
CREATE INDEX idx_ratings_rated_user ON ratings(rated_user);
CREATE INDEX idx_ratings_rated_by ON ratings(rated_by);
CREATE INDEX idx_ratings_score ON ratings(score);
CREATE UNIQUE INDEX idx_ratings_unique_per_task ON ratings(task_id, rated_by);
```

**Columns:**
- `rating_id` - Unique rating identifier
- `task_id` - Task being rated (FK)
- `rated_by` - User giving rating (FK)
- `rated_user` - User being rated (FK)
- `score` - Rating 1-5 stars
- `comment` - Optional review text (max 500 chars)
- `created_at` - When rating was given

**Constraints:**
- One rating per task per rater (UNIQUE constraint)
- Only allowed after task is completed
- Enforce in application logic

---

## 3. Key Relationships

### User → Task (1:Many)
- User creates multiple tasks
- User accepts multiple tasks
- Enforce: `tasks.created_by` FK to `users.user_id`
- Enforce: `tasks.accepted_by` FK to `users.user_id`

### Task → Proposal (1:Many)
- Task can have multiple proposals
- Enforce: `proposals.task_id` FK to `tasks.task_id`

### Task → Message (1:Many)
- Task conversation has multiple messages
- Enforce: `messages.task_id` FK to `tasks.task_id`

### Task → Payment (1:1)
- Each completed task has one payment
- Enforce: `payments.task_id` FK to `tasks.task_id` UNIQUE

### Task → Rating (1:Many)
- Task can have ratings from both poster and performer
- Enforce: `ratings.task_id` FK to `tasks.task_id`

---

## 4. Indexes for Performance

### Search Indexes
```sql
-- Find nearby tasks
CREATE INDEX idx_tasks_location ON tasks(latitude, longitude);

-- Find user's tasks
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_accepted_by ON tasks(accepted_by);

-- Filter by status
CREATE INDEX idx_tasks_status ON tasks(status);

-- Latest tasks
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

### Message Indexes
```sql
-- Get messages for a task conversation
CREATE INDEX idx_messages_task_id ON messages(task_id);

-- Find unread messages for recipient
CREATE INDEX idx_messages_read_at ON messages(read_at) WHERE read_at IS NULL;

-- Timeline of messages
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

### Payment Indexes
```sql
-- Track user earnings
CREATE INDEX idx_payments_performer_id ON payments(performer_id);

-- Track user expenses
CREATE INDEX idx_payments_poster_id ON payments(poster_id);

-- Payment status tracking
CREATE INDEX idx_payments_status ON payments(status);
```

### Rating Indexes
```sql
-- Get ratings for a user
CREATE INDEX idx_ratings_rated_user ON ratings(rated_user);

-- Prevent duplicate ratings per task
CREATE UNIQUE INDEX idx_ratings_unique_per_task ON ratings(task_id, rated_by);
```

---

## 5. Constraints & Triggers

### Data Integrity Constraints

```sql
-- Ensure locations are valid coordinates
ALTER TABLE users ADD CONSTRAINT check_user_location CHECK (
  (latitude IS NULL AND longitude IS NULL) OR
  (latitude IS NOT NULL AND longitude IS NOT NULL AND
   latitude >= -90 AND latitude <= 90 AND
   longitude >= -180 AND longitude <= 180)
);

ALTER TABLE tasks ADD CONSTRAINT check_task_location CHECK (
  latitude >= -90 AND latitude <= 90 AND
  longitude >= -180 AND longitude <= 180
);

-- Ensure prices are positive
ALTER TABLE tasks ADD CONSTRAINT check_task_prices CHECK (
  (accepted_price IS NULL OR accepted_price > 0) AND
  initial_price > 0
);

-- Ensure message is not empty
ALTER TABLE messages ADD CONSTRAINT check_message_text CHECK (
  length(trim(text)) > 0
);
```

### Auto-Update Timestamps

```sql
-- Create function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proposals_updated_at
BEFORE UPDATE ON proposals
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at
BEFORE UPDATE ON payments
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

### Update User Rating on New Rating

```sql
-- When rating is added, update user's average rating
CREATE OR REPLACE FUNCTION update_user_rating()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE users
  SET rating = (
    SELECT AVG(score)::DECIMAL(3,2)
    FROM ratings
    WHERE rated_user = NEW.rated_user
  ),
  rating_count = (
    SELECT COUNT(*)
    FROM ratings
    WHERE rated_user = NEW.rated_user
  )
  WHERE user_id = NEW.rated_user;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_rating_on_new_rating
AFTER INSERT ON ratings
FOR EACH ROW
EXECUTE FUNCTION update_user_rating();
```

---

## 6. Queries for Common Operations

### Find nearby tasks
```sql
SELECT * FROM tasks
WHERE status = 'open'
AND ST_Distance(
  ST_Point(longitude, latitude)::geography,
  ST_Point(-74.0060, 40.7128)::geography
) < 5000  -- 5km radius
ORDER BY created_at DESC
LIMIT 20;

-- Note: This requires PostGIS extension.
-- For basic implementation, calculate distance in application:
-- distance = sqrt((lat2-lat1)^2 + (lng2-lng1)^2) * 111
```

### Get user's task history
```sql
SELECT * FROM tasks
WHERE created_by = $1 OR accepted_by = $1
ORDER BY created_at DESC
LIMIT 50;
```

### Get user's earnings
```sql
SELECT
  SUM(amount) as total_earned,
  COUNT(*) as completed_tasks
FROM payments
WHERE performer_id = $1
AND status = 'released';
```

### Get conversation with unread count
```sql
SELECT
  t.task_id,
  t.title,
  COUNT(CASE WHEN m.read_at IS NULL THEN 1 END) as unread_count,
  MAX(m.created_at) as last_message_time
FROM tasks t
LEFT JOIN messages m ON t.task_id = m.task_id
WHERE t.task_id = $1
GROUP BY t.task_id, t.title;
```

### Get user's average rating with distribution
```sql
SELECT
  COUNT(*) as total_ratings,
  AVG(score)::DECIMAL(3,2) as average_rating,
  SUM(CASE WHEN score = 5 THEN 1 ELSE 0 END) as stars_5,
  SUM(CASE WHEN score = 4 THEN 1 ELSE 0 END) as stars_4,
  SUM(CASE WHEN score = 3 THEN 1 ELSE 0 END) as stars_3,
  SUM(CASE WHEN score = 2 THEN 1 ELSE 0 END) as stars_2,
  SUM(CASE WHEN score = 1 THEN 1 ELSE 0 END) as stars_1
FROM ratings
WHERE rated_user = $1;
```

### Platform metrics
```sql
SELECT
  (SELECT COUNT(*) FROM users) as total_users,
  (SELECT COUNT(*) FROM tasks) as total_tasks,
  (SELECT COUNT(*) FROM tasks WHERE status = 'completed') as completed_tasks,
  (SELECT COUNT(*) FROM tasks WHERE status = 'completed')::DECIMAL /
    NULLIF((SELECT COUNT(*) FROM tasks), 0) as completion_rate,
  (SELECT COUNT(DISTINCT created_by) FROM tasks WHERE created_at > NOW() - INTERVAL '1 day') as active_posters,
  (SELECT COUNT(DISTINCT accepted_by) FROM tasks WHERE created_at > NOW() - INTERVAL '1 day') as active_performers,
  (SELECT AVG(rating)::DECIMAL(3,2) FROM users) as avg_platform_rating;
```

---

## 7. Initial Setup Script

```sql
-- Create database
CREATE DATABASE doitforme;

-- Connect to database
\c doitforme

-- Enable extensions (if using PostGIS for better geospatial queries)
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables (see Table Definitions above)
CREATE TABLE users ( ... );
CREATE TABLE tasks ( ... );
CREATE TABLE proposals ( ... );
CREATE TABLE messages ( ... );
CREATE TABLE payments ( ... );
CREATE TABLE ratings ( ... );

-- Create all indexes
-- Create all triggers
-- Create all constraints

-- Verify tables created
\dt

-- Verify indexes
\di
```

---

## 8. Backup & Maintenance

### Backup
```bash
pg_dump doitforme > doitforme_backup.sql
```

### Restore
```bash
createdb doitforme_restored
psql doitforme_restored < doitforme_backup.sql
```

### Monitor Table Sizes
```sql
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 9. Data Type Reference

| Type | Usage | Example |
|------|-------|---------|
| `UUID` | Unique IDs | `gen_random_uuid()` |
| `VARCHAR(n)` | Text with max length | Emails, names, titles |
| `TEXT` | Unlimited text | Descriptions, comments |
| `DECIMAL(10,2)` | Money/prices | $99.99 |
| `INTEGER` | Whole numbers | Count, status codes |
| `BOOLEAN` | True/False | Flags |
| `TIMESTAMP WITH TIME ZONE` | DateTime (UTC) | Logs, created_at |
| `DECIMAL(10,8)` | GPS coordinates | Latitude/longitude |

---

## 10. Connection String

```
postgresql://username:password@localhost:5432/doitforme
```

### Python Connection (psycopg2)
```python
import psycopg2

conn = psycopg2.connect(
  host="localhost",
  database="doitforme",
  user="postgres",
  password="your_password",
  port="5432"
)
```

### SQLAlchemy
```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:password@localhost/doitforme')
```

---

**Database Schema Version:** 1.0
**Last Updated:** 2026-03-18
**Status:** Ready for implementation
**Next Step:** Create table creation SQL scripts and implement ORM models
