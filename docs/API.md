# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

### Register User
**POST** `/api/auth/register`

Request body:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response:
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com"
  }
}
```

### Login
**POST** `/api/auth/login`

Request body:
```json
{
  "username": "admin",
  "password": "Admin@1234"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@truthguard.ai"
  }
}
```

### Verify Token
**GET** `/api/auth/verify`

Headers:
```
Authorization: Bearer {access_token}
```

Response:
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@truthguard.ai",
    "is_active": true,
    "is_admin": true
  }
}
```

## Analysis

### Analyze News (Predict)
**POST** `/api/analysis/predict`

Request body:
```json
{
  "text": "Breaking news: Scientists discover new cure for disease",
  "source_type": "article"
}
```

OR with URL:
```json
{
  "url": "https://example.com/news/article",
  "source_type": "url"
}
```

Response:
```json
{
  "prediction": "Real",
  "confidence": 87.5,
  "probabilities": {
    "real": 87.5,
    "fake": 12.5
  },
  "reasons": [
    "Uses credible sources",
    "Scientific terminology detected"
  ],
  "source_type": "article",
  "processing_time": 145.23
}
```

### Get Analysis History
**GET** `/api/analysis/`

Headers:
```
Authorization: Bearer {access_token}
```

Response:
```json
[
  {
    "id": 1,
    "prediction": "Real",
    "confidence": 87.5,
    "text_preview": "Breaking news: Scientists discover...",
    "created_at": "2026-04-07T10:30:00Z"
  }
]
```

## Health & Status

### Health Check
**GET** `/api/health`

Response:
```json
{
  "status": "ok",
  "message": "API is healthy"
}
```

### API Root Info
**GET** `/api/`

Response:
```json
{
  "message": "Fake News Detection API is running",
  "version": "2.0",
  "endpoints": [
    "/api/health",
    "/api/predict",
    "/api/auth/register",
    "/api/auth/login",
    "/api/analysis/"
  ]
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP Status Codes:
- `200 OK` - Successful request
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Invalid/missing authentication
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

The API implements rate limiting:
- Default: 100 requests per hour per IP

Rate limit info is included in response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1617852000
```
