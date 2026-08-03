# API Design

## Purpose

Defines how external clients communicate with DecisionOS.

---

# API Style

- RESTful API
- JSON request/response
- Stateless communication
- Versioned endpoints
- Resource-oriented design

---

# API Resources

| Resource | Description |
|----------|-------------|
| Authentication | User authentication and authorization |
| Users | User account management |
| Profile | User profile and preferences |
| Decisions | Decision lifecycle management |
| Documents | User uploaded documents |
| Integrations | Connected third-party services |

---

# Resource Operations

| Resource | Operations |
|----------|------------|
| Authentication | Login, Logout, Refresh Token |
| Users | Create, Read, Update |
| Profile | Read, Update |
| Decisions | Create, Read, Update, Archive, Re-evaluate |
| Documents | Upload, Read, Delete |
| Integrations | Connect, Disconnect, Sync |

---

# Request Flow

```text
Client
    │
    ▼
REST API
    │
    ▼
Application Layer
    │
    ▼
Business Module
    │
    ▼
Database / AI Services
    │
    ▼
Response
```

---

# Authentication

- JWT Access Token
- Refresh Token
- Protected endpoints require authentication

---

# Response Format

## Success

```json
{
  "success": true,
  "data": {}
}
```

## Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request."
  }
}
```

---

# API Versioning

```
/api/v1
```

Breaking changes will be introduced through a new version.

---

# HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Resource Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Resource Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

# Design Principles

- Consistent naming conventions
- Predictable request/response structure
- Resource-oriented endpoints
- Stateless APIs
- Clear validation errors
- Backward compatibility within the same API version