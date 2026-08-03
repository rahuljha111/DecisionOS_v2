# Data Architecture

## Purpose

Defines how DecisionOS stores, retrieves, and manages application data.

---

# Data Categories

| Data | Storage |
|-------|---------|
| User Data | PostgreSQL |
| Decision Data | PostgreSQL |
| Memory | PostgreSQL |
| Documents | Local Storage / Object Storage |
| Cache | Redis (Optional) |

---

# User Data

Stores long-term user information.

Examples

- Account
- Profile
- Goals
- Preferences
- Integrations

---

# Decision Data

Stores everything related to a decision.

Examples

- Decision
- Context
- Options
- Evaluations
- Recommendation
- Outcome

---

# Memory

Stores reusable information.

Examples

- Decision History
- User Facts
- Previous Outcomes

For V1, memory is stored in PostgreSQL.

---

# Documents

Stores files uploaded by users.

Examples

- Resume
- Offer Letter
- Medical Reports
- Certificates

Initially stored locally during development.

Can be migrated to S3 or Cloud Storage later.

---

# Cache

Stores temporary data.

Examples

- Sessions
- Frequently accessed data
- API responses

Redis is optional for V1 and can be introduced when needed.

---

# Data Relationships

```text
User
 │
 ├── Profile
 ├── Goals
 ├── Decisions
 │       │
 │       ├── Context
 │       ├── Options
 │       ├── Evaluation
 │       ├── Recommendation
 │       └── Outcome
 │
 └── Documents
```

---

# Data Principles

- PostgreSQL is the primary data store.
- Avoid duplicate information.
- Keep data normalized where practical.
- Store only data required by the application.
- Separate business data from AI-generated content.

---

# Future Enhancements

The following may be added later:

- pgvector for semantic search
- Object Storage (S3/GCS)
- Redis caching
- Event streaming