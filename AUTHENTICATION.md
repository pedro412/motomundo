# Authentication API Documentation

## Overview

The Motomundo authentication system provides secure user registration, login, and token-based authentication using Django REST Framework's token authentication.

## Authentication Endpoints

All authentication endpoints are available under `/api/auth/`

### 1. User Registration

**Endpoint**: `POST /api/auth/register/`  
**Permission**: Public (no authentication required)

Register a new user account.

**Request Body**:
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Required Fields**:
- `username`: Unique username (case-insensitive)
- `email`: Valid email address (unique, case-insensitive)
- `password`: Minimum 8 characters, validated against Django's password validators
- `password_confirm`: Must match password

**Optional Fields**:
- `first_name`: User's first name
- `last_name`: User's last name

**Response** (201 Created):
```json
{
    "user": {
        "id": 7,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "date_joined": "2025-08-13T00:17:35.262261Z"
    },
    "token": "de7615a19523ca74656a688daae6d8114e503a96",
    "message": "Registration successful"
}
```

**Error Response** (400 Bad Request):
```json
{
    "username": ["A user with this username already exists."],
    "email": ["A user with this email already exists."],
    "password_confirm": ["Passwords do not match."]
}
```

### 2. User Login

**Endpoint**: `POST /api/auth/login/`  
**Permission**: Public (no authentication required)

Authenticate user and receive access token.

**Request Body**:
```json
{
    "username": "john_doe",
    "password": "securepass123"
}
```

**Response** (200 OK):
```json
{
    "user": {
        "id": 7,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "date_joined": "2025-08-13T00:17:35.262261Z"
    },
    "token": "de7615a19523ca74656a688daae6d8114e503a96",
    "message": "Login successful"
}
```

### 3. User Profile

**Endpoint**: `GET /api/auth/profile/`  
**Permission**: Authenticated users only

Get current user's profile information.

**Headers**:
```
Authorization: Token de7615a19523ca74656a688daae6d8114e503a96
```

**Response** (200 OK):
```json
{
    "id": 7,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "date_joined": "2025-08-13T00:17:35.262261Z"
}
```

**Update Profile**: `PUT /api/auth/profile/`

**Request Body**:
```json
{
    "email": "newemail@example.com",
    "first_name": "Updated",
    "last_name": "Name"
}
```

### 4. Change Password

**Endpoint**: `PUT /api/auth/change-password/`  
**Permission**: Authenticated users only

Change user's password.

**Request Body**:
```json
{
    "old_password": "currentpass123",
    "new_password": "newsecurepass123",
    "new_password_confirm": "newsecurepass123"
}
```

**Response** (200 OK):
```json
{
    "message": "Password changed successfully",
    "token": "new_token_here_after_password_change"
}
```

### 5. User Permissions

**Endpoint**: `GET /api/auth/permissions/`  
**Permission**: Authenticated users only

Get current user's roles and permissions.

**Response** (200 OK):
```json
{
    "user": {
        "id": 7,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "date_joined": "2025-08-13T00:17:35.262261Z"
    },
    "is_superuser": false,
    "roles": {
        "club_admin": [
            {
                "club_id": 1,
                "club_name": "Harley Riders United"
            }
        ],
        "chapter_manager": [
            {
                "chapter_id": 1,
                "chapter_name": "San Francisco Chapter",
                "club_name": "Harley Riders United"
            }
        ]
    },
    "permissions": {
        "manageable_clubs_count": 1,
        "manageable_chapters_count": 2
    }
}
```

### 6. Logout

**Endpoint**: `POST /api/auth/logout/`  
**Permission**: Authenticated users only

Logout user by invalidating their authentication token.

**Response** (200 OK):
```json
{
    "message": "Logout successful"
}
```

## Authentication Methods

### Token Authentication (Recommended for API)

Include the token in the Authorization header:
```
Authorization: Token de7615a19523ca74656a688daae6d8114e503a96
```

### Session Authentication (for web interface)

Standard Django session authentication for web pages.

### Basic Authentication (development only)

Username/password authentication for development and testing.

## Security Features

### Password Validation
- Minimum 8 characters
- Cannot be too similar to personal information
- Cannot be a commonly used password
- Cannot be entirely numeric

### Email and Username Uniqueness
- Case-insensitive unique constraints
- Proper validation and error messages

### Token Security
- Tokens are automatically generated on registration/login
- Tokens are invalidated on logout
- New token generated when password changes

### Rate Limiting (recommended for production)
Consider implementing rate limiting for authentication endpoints to prevent brute force attacks.

## Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "New",
    "last_name": "User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepass123"
  }'
```

### Access protected endpoint
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token your_token_here"
```

### Access clubs API with authentication
```bash
curl -X GET http://localhost:8000/api/clubs/ \
  -H "Authorization: Token your_token_here"
```

## Error Codes

- **400 Bad Request**: Invalid data, validation errors
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Permission denied
- **409 Conflict**: Resource already exists (duplicate username/email)

## Best Practices

1. **Store tokens securely** on the client side
2. **Use HTTPS** in production to protect tokens in transit
3. **Implement token refresh** for long-lived applications
4. **Handle token expiration** gracefully in client applications
5. **Validate user input** on the client side for better UX
6. **Implement rate limiting** to prevent abuse
