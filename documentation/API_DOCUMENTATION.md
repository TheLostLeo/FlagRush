# FlagRush CTF Backend API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Interactive Documentation
FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Response Format
All API responses follow this standardized format:

### Success Response
```json
{
    "success": true,
    "message": "Success message",
    "data": {
        // Response data here
    }
}
```

### Error Response
```json
{
    "success": false,
    "message": "Error message",
    "details": {
        // Additional error details (optional)
    }
}
```

---

## Authentication Endpoints

### Register User
**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secure_password"
}
```

**Response (201):**
```json
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "is_admin": false,
        "created_at": "2025-09-04T10:30:00Z",
        "last_login": null
    }
}
```

**Error Responses:**
- `400` - Missing required fields
- `409` - Username or email already exists

---

### Login User
**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "secure_password"
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "is_admin": false,
            "created_at": "2025-09-04T10:30:00Z",
            "last_login": "2025-09-04T11:00:00Z"
        },
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**Error Responses:**
- `400` - Missing required fields
- `401` - Invalid credentials

---

### Get User Profile
**GET** `/api/auth/profile`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "is_admin": false,
        "created_at": "2025-09-04T10:30:00Z",
        "last_login": "2025-09-04T11:00:00Z"
    }
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `404` - User not found

---

### Update User Profile
**PUT** `/api/auth/profile`

Update current user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
    "email": "newemail@example.com",
    "password": "new_password"
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "data": {
        "id": 1,
        "username": "johndoe",
        "email": "newemail@example.com",
        "is_admin": false,
        "created_at": "2025-09-04T10:30:00Z",
        "last_login": "2025-09-04T11:00:00Z"
    }
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `409` - Email already exists

---

## Challenge Endpoints

### Get All Challenges
**GET** `/api/challenges/`

Get all active challenges.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "id": 1,
            "title": "Welcome Challenge",
            "description": "A simple welcome challenge to get you started.",
            "category": "misc",
            "points": 50,
            "author": "CTF Admin",
            "is_active": true,
            "created_at": "2025-09-04T10:00:00Z",
            "file_url": null,
            "hint_1": "This is just a welcome message!",
            "hint_2": null,
            "hint_3": null,
            "solve_count": 5
        },
        {
            "id": 2,
            "title": "Basic Web Challenge",
            "description": "Find the hidden flag in this simple web page.",
            "category": "web",
            "points": 100,
            "author": "CTF Admin",
            "is_active": true,
            "created_at": "2025-09-04T10:00:00Z",
            "file_url": null,
            "hint_1": "Try looking at the page source",
            "hint_2": null,
            "hint_3": null,
            "solve_count": 3
        }
    ]
}
```

**Error Responses:**
- `401` - Invalid or missing token

---

### Get Specific Challenge
**GET** `/api/challenges/<challenge_id>`

Get details of a specific challenge.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": {
        "id": 1,
        "title": "Welcome Challenge",
        "description": "A simple welcome challenge to get you started.",
        "category": "misc",
        "points": 50,
        "author": "CTF Admin",
        "is_active": true,
        "created_at": "2025-09-04T10:00:00Z",
        "file_url": null,
        "hint_1": "This is just a welcome message!",
        "hint_2": null,
        "hint_3": null,
        "solve_count": 5
    }
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `404` - Challenge not found

---

### Create Challenge (Admin Only)
**POST** `/api/challenges/`

Create a new challenge.

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Request Body:**
```json
{
    "title": "New Challenge",
    "description": "Challenge description here",
    "category": "web",
    "points": 200,
    "flag": "flag{example_flag}",
    "author": "Admin User",
    "file_url": "https://example.com/file.zip",
    "hint_1": "First hint",
    "hint_2": "Second hint",
    "hint_3": "Third hint"
}
```

**Response (201):**
```json
{
    "success": true,
    "message": "Challenge created successfully",
    "data": {
        "id": 3,
        "title": "New Challenge",
        "description": "Challenge description here",
        "category": "web",
        "points": 200,
        "flag": "flag{example_flag}",
        "author": "Admin User",
        "is_active": true,
        "created_at": "2025-09-04T12:00:00Z",
        "file_url": "https://example.com/file.zip",
        "hint_1": "First hint",
        "hint_2": "Second hint",
        "hint_3": "Third hint",
        "solve_count": 0
    }
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `403` - Admin privileges required
- `400` - Missing required fields

---

### Update Challenge (Admin Only)
**PUT** `/api/challenges/<challenge_id>`

Update an existing challenge.

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Request Body:**
```json
{
    "title": "Updated Challenge Title",
    "points": 250,
    "is_active": false
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "Challenge updated successfully",
    "data": {
        "id": 3,
        "title": "Updated Challenge Title",
        "description": "Challenge description here",
        "category": "web",
        "points": 250,
        "flag": "flag{example_flag}",
        "author": "Admin User",
        "is_active": false,
        "created_at": "2025-09-04T12:00:00Z",
        "file_url": "https://example.com/file.zip",
        "hint_1": "First hint",
        "hint_2": "Second hint",
        "hint_3": "Third hint",
        "solve_count": 0
    }
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `403` - Admin privileges required
- `404` - Challenge not found

---

### Delete Challenge (Admin Only)
**DELETE** `/api/challenges/<challenge_id>`

Delete a challenge.

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Challenge deleted successfully"
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `403` - Admin privileges required
- `404` - Challenge not found

---

### Get Challenge Categories
**GET** `/api/challenges/categories`

Get all unique challenge categories.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": [
        "misc",
        "web",
        "crypto",
        "pwn",
        "reverse",
        "forensics"
    ]
}
```

**Error Responses:**
- `401` - Invalid or missing token

---

## 🚩 Submission Endpoints

### Submit Flag
**POST** `/api/submissions/`

Submit a flag for a challenge.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
    "challenge_id": 1,
    "flag": "flag{welcome_to_ctf}"
}
```

**Response (200) - Correct Flag:**
```json
{
    "success": true,
    "message": "Correct flag! Well done!",
    "data": {
        "submission": {
            "id": 1,
            "user_id": 1,
            "challenge_id": 1,
            "submitted_flag": "flag{welcome_to_ctf}",
            "is_correct": true,
            "submitted_at": "2025-09-04T12:30:00Z"
        },
        "is_correct": true,
        "points_earned": 50
    }
}
```

**Response (200) - Incorrect Flag:**
```json
{
    "success": true,
    "message": "Incorrect flag. Try again!",
    "data": {
        "submission": {
            "id": 2,
            "user_id": 1,
            "challenge_id": 1,
            "submitted_flag": "flag{wrong_flag}",
            "is_correct": false,
            "submitted_at": "2025-09-04T12:35:00Z"
        },
        "is_correct": false,
        "points_earned": 0
    }
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `400` - Missing required fields or challenge already solved
- `404` - Challenge not found

---

### Get User Submissions
**GET** `/api/submissions/user`

Get all submissions for the current user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "id": 1,
            "user_id": 1,
            "challenge_id": 1,
            "submitted_flag": "flag{welcome_to_ctf}",
            "is_correct": true,
            "submitted_at": "2025-09-04T12:30:00Z",
            "challenge_title": "Welcome Challenge",
            "challenge_points": 50
        },
        {
            "id": 2,
            "user_id": 1,
            "challenge_id": 2,
            "submitted_flag": "flag{wrong_flag}",
            "is_correct": false,
            "submitted_at": "2025-09-04T12:35:00Z",
            "challenge_title": "Basic Web Challenge",
            "challenge_points": 100
        }
    ]
}
```

**Error Responses:**
- `401` - Invalid or missing token

---

### Get Challenge Submissions
**GET** `/api/submissions/challenge/<challenge_id>`

Get user's submissions for a specific challenge.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "id": 2,
            "user_id": 1,
            "challenge_id": 2,
            "submitted_flag": "flag{wrong_flag}",
            "is_correct": false,
            "submitted_at": "2025-09-04T12:35:00Z"
        },
        {
            "id": 3,
            "user_id": 1,
            "challenge_id": 2,
            "submitted_flag": "flag{correct_flag}",
            "is_correct": true,
            "submitted_at": "2025-09-04T12:40:00Z"
        }
    ]
}
```

**Error Responses:**
- `401` - Invalid or missing token

---

### Get All Submissions (Admin Only)
**GET** `/api/submissions/all`

Get all submissions from all users.

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "id": 1,
            "user_id": 1,
            "challenge_id": 1,
            "submitted_flag": "flag{welcome_to_ctf}",
            "is_correct": true,
            "submitted_at": "2025-09-04T12:30:00Z",
            "username": "johndoe",
            "challenge_title": "Welcome Challenge",
            "challenge_points": 50
        },
        {
            "id": 2,
            "user_id": 2,
            "challenge_id": 1,
            "submitted_flag": "flag{wrong_flag}",
            "is_correct": false,
            "submitted_at": "2025-09-04T12:35:00Z",
            "username": "janedoe",
            "challenge_title": "Welcome Challenge",
            "challenge_points": 50
        }
    ]
}
```

**Error Responses:**
- `401` - Invalid or missing token
- `403` - Admin privileges required

---

### Get Submission Statistics
**GET** `/api/submissions/stats`

Get submission statistics for the current user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": {
        "total_submissions": 10,
        "correct_submissions": 3,
        "incorrect_submissions": 7,
        "current_score": 350,
        "accuracy": 30.0
    }
}
```

**Error Responses:**
- `401` - Invalid or missing token

---

### Get Leaderboard
**GET** `/api/submissions/leaderboard`

Get the user leaderboard sorted by score.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "id": 1,
            "username": "johndoe",
            "score": 350,
            "solved_challenges": 3
        },
        {
            "id": 2,
            "username": "janedoe",
            "score": 250,
            "solved_challenges": 2
        },
        {
            "id": 3,
            "username": "bobsmith",
            "score": 150,
            "solved_challenges": 1
        }
    ]
}
```

**Error Responses:**
- `401` - Invalid or missing token

---

## 🏠 General Endpoints

### API Root
**GET** `/`

Get API information and available endpoints.

**Response (200):**
```json
{
    "message": "CTF Backend API",
    "version": "1.0.0",
    "endpoints": {
        "auth": "/api/auth",
        "challenges": "/api/challenges",
        "submissions": "/api/submissions"
    }
}
```

---

### Health Check
**GET** `/health`

Check API health status.

**Response (200):**
```json
{
    "status": "healthy",
    "database": "connected"
}
```

---

## Notes

### Authentication
- JWT tokens expire after 1 hour by default (configurable via `JWT_ACCESS_TOKEN_EXPIRES`)
- Admin privileges are required for challenge management endpoints
- Include the token in the `Authorization` header as `Bearer <token>`

### Rate Limiting
- Currently no rate limiting is implemented
- Consider implementing rate limiting for production use

### Error Codes
- `200` - Success
- `201` - Created successfully
- `400` - Bad request (missing fields, validation errors)
- `401` - Unauthorized (invalid or missing token)
- `403` - Forbidden (insufficient privileges)
- `404` - Not found
- `409` - Conflict (duplicate data)
- `500` - Internal server error

### Data Validation
- All required fields must be provided in request bodies
- Email addresses must be valid format
- Usernames must be unique
- Passwords are hashed using bcrypt

### Flag Format
- Flags can be in any format (commonly `flag{...}`)
- Flag comparison is case-sensitive and whitespace-sensitive
- Consider implementing flexible flag validation in future versions
