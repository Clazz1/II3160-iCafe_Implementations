# iCafe Platform API - Authentication Guide

This guide shows how to use the JWT authentication system that has been added to the iCafe API.

## Prerequisites

Install the required dependencies:

```bash
pip install -r app/requirements.txt
```

## Starting the Server

```bash
cd app
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Authentication Endpoints

### 1. Register a New User

```bash
POST /auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "testuser@example.com", 
    "password": "securepassword123",
    "role": "CUSTOMER"
}
```

Response:
```json
{
    "id": "user-uuid",
    "username": "testuser", 
    "email": "testuser@example.com",
    "role": "CUSTOMER",
    "status": "ACTIVE"
}
```

### 2. Login

```bash
POST /auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "securepassword123"
}
```

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 3. Get Current User Info

```bash
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:
```json
{
    "id": "user-uuid",
    "username": "testuser",
    "email": "testuser@example.com", 
    "role": "CUSTOMER",
    "status": "ACTIVE"
}
```

## Protected Endpoints

All existing API endpoints now require authentication. Include the JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Examples:

#### Create Reservation
```bash
POST /reservations
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
    "customer_id": "customer123",
    "workstation_id": "ws001",
    "start": "2025-12-01T10:00:00",
    "end": "2025-12-01T12:00:00",
    "package_name": "Gaming Package",
    "package_duration_minutes": 120,
    "package_price_amount": 50000
}
```

#### List Reservations
```bash
GET /reservations
Authorization: Bearer <your-jwt-token>
```

#### Start Session
```bash
POST /sessions
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
    "customer_id": "customer123",
    "workstation_id": "ws001",
    "reservation_id": "reservation-uuid"
}
```

## User Roles

- `CUSTOMER`: Regular user with access to create reservations, sessions, etc.
- `ADMIN`: Admin user with elevated privileges (can be extended for admin-only endpoints)

## Security Configuration

- JWT tokens expire after 30 minutes by default
- Passwords are hashed using bcrypt
- Secret key should be changed in production (currently set in `auth_service.py`)

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with Swagger UI.

## Testing Authentication

1. Register a new user with the `/auth/register` endpoint
2. Login with the `/auth/login` endpoint to get a JWT token  
3. Use the token in the Authorization header for all subsequent requests
4. Try accessing protected endpoints like `/reservations`, `/sessions`, `/invoices`

All endpoints will return `401 Unauthorized` if no valid token is provided.