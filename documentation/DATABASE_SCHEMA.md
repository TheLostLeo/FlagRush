# FlagRush CTF Backend - Database Schema Documentation

## Overview
This document describes the database schema for the FlagRush CTF backend application. The application uses PostgreSQL as the primary database with SQLAlchemy ORM for database operations.

## Database Configuration
- **Database Engine**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migration Support**: Alembic (if needed)
- **Connection Pool**: SQLAlchemy connection pooling

## Table of Contents
- [Users Table](#users-table)
- [Challenges Table](#challenges-table)
- [Submissions Table](#submissions-table)
- [Relationships](#relationships)
- [Indexes](#indexes)
- [Constraints](#constraints)

## Users Table

### Table: `users`
Stores user account information and authentication data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `username` | VARCHAR(80) | UNIQUE, NOT NULL, INDEX | User's login name |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL, INDEX | User's email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `is_admin` | BOOLEAN | DEFAULT FALSE | Admin privilege flag |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| `last_login` | TIMESTAMP | NULLABLE | Last login timestamp |

### Example Data:
```sql
INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES
('admin', 'admin@ctf.local', '$2b$12$...', true, '2025-09-06 10:00:00'),
('player1', 'player1@example.com', '$2b$12$...', false, '2025-09-06 11:00:00');
```

## Challenges Table

### Table: `challenges`
Stores CTF challenge information including flags and metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique challenge identifier |
| `title` | VARCHAR(200) | NOT NULL | Challenge title |
| `description` | TEXT | NOT NULL | Challenge description |
| `category` | VARCHAR(50) | NOT NULL | Challenge category (web, crypto, pwn, etc.) |
| `points` | INTEGER | NOT NULL | Points awarded for solving |
| `flag` | VARCHAR(500) | NOT NULL | Correct flag value |
| `author` | VARCHAR(100) | NULLABLE | Challenge author name |
| `is_active` | BOOLEAN | DEFAULT TRUE | Challenge visibility status |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Challenge creation time |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last modification time |
| `file_url` | VARCHAR(500) | NULLABLE | URL to challenge files |
| `hint_1` | TEXT | NULLABLE | First hint |
| `hint_2` | TEXT | NULLABLE | Second hint |
| `hint_3` | TEXT | NULLABLE | Third hint |

### Challenge Categories:
- `web` - Web application security
- `crypto` - Cryptography challenges
- `pwn` - Binary exploitation
- `reverse` - Reverse engineering
- `forensics` - Digital forensics
- `misc` - Miscellaneous challenges

### Example Data:
```sql
INSERT INTO challenges (title, description, category, points, flag, author, is_active) VALUES
('SQL Injection Basics', 'Find the hidden flag in this vulnerable web app', 'web', 100, 'flag{sql_injection_found}', 'Admin', true),
('Caesar Cipher', 'Decode this simple cipher', 'crypto', 50, 'flag{caesar_decoded}', 'Admin', true);
```

## Submissions Table

### Table: `submissions`
Stores all flag submission attempts with results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique submission identifier |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | User who submitted |
| `challenge_id` | INTEGER | FOREIGN KEY (challenges.id), NOT NULL | Challenge being attempted |
| `submitted_flag` | VARCHAR(500) | NOT NULL | Flag value submitted |
| `is_correct` | BOOLEAN | NOT NULL | Whether submission was correct |
| `submitted_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Submission timestamp |

### Example Data:
```sql
INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct, submitted_at) VALUES
(2, 1, 'flag{sql_injection_found}', true, '2025-09-06 12:00:00'),
(2, 1, 'flag{wrong_flag}', false, '2025-09-06 11:55:00');
```

## Relationships

### Entity Relationship Diagram
```
Users (1) ←→ (N) Submissions (N) ←→ (1) Challenges
```

### Foreign Key Relationships:

1. **submissions.user_id → users.id**
   - One user can have many submissions
   - Cascade: ON DELETE CASCADE (remove submissions when user deleted)

2. **submissions.challenge_id → challenges.id**
   - One challenge can have many submissions
   - Cascade: ON DELETE CASCADE (remove submissions when challenge deleted)

### SQLAlchemy Relationships:
```python
# User model
submissions = relationship("Submission", back_populates="user")

# Challenge model
submissions = relationship("Submission", back_populates="challenge")

# Submission model
user = relationship("User", back_populates="submissions")
challenge = relationship("Challenge", back_populates="submissions")
```

## Indexes

### Primary Indexes:
- `users.id` (PRIMARY KEY)
- `challenges.id` (PRIMARY KEY)
- `submissions.id` (PRIMARY KEY)

### Secondary Indexes:
- `users.username` (UNIQUE INDEX)
- `users.email` (UNIQUE INDEX)
- `submissions.user_id` (FOREIGN KEY INDEX)
- `submissions.challenge_id` (FOREIGN KEY INDEX)

### Recommended Additional Indexes:
```sql
-- For performance on common queries
CREATE INDEX idx_submissions_user_challenge ON submissions(user_id, challenge_id);
CREATE INDEX idx_submissions_correct ON submissions(is_correct);
CREATE INDEX idx_challenges_category ON challenges(category);
CREATE INDEX idx_challenges_active ON challenges(is_active);
```

## Constraints

### Unique Constraints:
- `users.username` - No duplicate usernames
- `users.email` - No duplicate email addresses

### Check Constraints:
```sql
-- Ensure points are positive
ALTER TABLE challenges ADD CONSTRAINT check_points_positive CHECK (points > 0);

-- Ensure valid categories
ALTER TABLE challenges ADD CONSTRAINT check_valid_category 
CHECK (category IN ('web', 'crypto', 'pwn', 'reverse', 'forensics', 'misc'));
```

### Foreign Key Constraints:
- `submissions.user_id` references `users.id`
- `submissions.challenge_id` references `challenges.id`

## Database Initialization

### Setup Script:
The database is initialized using `init_db.py` which:
1. Creates all tables using SQLAlchemy metadata
2. Creates default admin user
3. Optionally seeds sample challenges

### Sample Initialization:
```python
# Create tables
Base.metadata.create_all(bind=engine)

# Create admin user
admin_user = User(
    username="admin",
    email="admin@ctf.local",
    is_admin=True
)
admin_user.set_password("admin_password")
```

## Performance Considerations

### Query Optimization:
- Use indexes on frequently queried columns
- Implement pagination for large result sets
- Consider read replicas for high-traffic scenarios

### Common Queries:
```sql
-- Get user's correct submissions
SELECT c.title, c.points, s.submitted_at 
FROM submissions s 
JOIN challenges c ON s.challenge_id = c.id 
WHERE s.user_id = ? AND s.is_correct = true;

-- Get challenge leaderboard
SELECT u.username, COUNT(*) as solves, SUM(c.points) as total_points
FROM submissions s 
JOIN users u ON s.user_id = u.id 
JOIN challenges c ON s.challenge_id = c.id 
WHERE s.is_correct = true 
GROUP BY u.id 
ORDER BY total_points DESC;
```

## Security Considerations

### Password Security:
- Passwords stored as bcrypt hashes
- Minimum password complexity enforced at application level

### Flag Security:
- Flags stored in plaintext (consider encryption for highly sensitive CTFs)
- Access restricted to admin users only

### Data Integrity:
- Foreign key constraints prevent orphaned records
- Unique constraints prevent duplicate users
- Timestamps track all modifications

## Migration Strategy

### Schema Changes:
For production deployments, use Alembic for database migrations:
```bash
# Generate migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head
```

### Backup Strategy:
- Regular PostgreSQL dumps
- Point-in-time recovery capability
- Test restoration procedures
