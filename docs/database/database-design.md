# Database Design

## Purpose

Defines the primary data model and storage strategy for DecisionOS.

Version 1 uses a single PostgreSQL database.

---

# Database

| Database | Purpose |
|----------|---------|
| PostgreSQL | Primary application database |

---

# Core Entities

| Entity | Purpose |
|---------|---------|
| User | Authentication and account information |
| Profile | Long-term user information |
| Goal | User goals and objectives |
| Decision | User decision |
| Option | Possible solutions |
| Evaluation | Analysis of an option |
| Recommendation | Final recommendation |
| Outcome | Actual result after user action |
| Document | Uploaded files |
| Integration | Connected external services |

---

# High-Level Relationships

```text
User
│
├── Profile (1:1)
├── Goals (1:N)
├── Decisions (1:N)
├── Documents (1:N)
└── Integrations (1:N)

Decision
│
├── Options (1:N)
├── Evaluations (1:N)
├── Recommendation (1:1)
└── Outcome (0:1)
```

---

# Common Fields

Every table should contain:

- id (UUID)
- created_at
- updated_at

Optional:

- deleted_at
- metadata (JSONB)

---

# Storage Principles

- PostgreSQL is the single source of truth.
- Normalize business data.
- Use JSONB only for flexible metadata.
- Avoid duplicate information.
- Store only required business data.

---

# Future Extensions

Future versions may introduce:

- pgvector
- Redis
- Object Storage
- Analytics Database

naming conventions
Tables        : snake_case plural
Columns       : snake_case
Primary Key   : id
Foreign Keys  : <table>_id

Delete rules
| Parent   | Child          | Action  |
| -------- | -------------- | ------- |
| User     | Profile        | CASCADE |
| User     | Goals          | CASCADE |
| User     | Decisions      | CASCADE |
| Decision | Context        | CASCADE |
| Decision | Options        | CASCADE |
| Option   | Evaluations    | CASCADE |
| Decision | Recommendation | CASCADE |


                                    USERS
────────────────────────────────────────────────────────────────────
PK  id
    email (UNIQUE)
    password_hash
    auth_provider
    email_verified
    is_active
    last_login_at
    created_at
    updated_at
────────────────────────────────────────────────────────────────────
        │
        ├──────────────┬──────────────┬──────────────┬──────────────┐
        │              │              │              │              │
      1 │            1:N            1:N            1:N            1:N
        ▼              ▼              ▼              ▼              ▼

USER_PROFILES      GOALS       DECISIONS      DOCUMENTS     INTEGRATIONS


GOALS
──────────────────────────────
PK id
FK user_id

title
description
status

created_at
updated_at


DECISIONS
──────────────────────────────
PK id
FK user_id

title
description
category
status
priority

completed_at

created_at
updated_at

DECISION_CONTEXTS
──────────────────────────────
PK id
FK decision_id (UNIQUE)

context_data JSONB

created_at
updated_at

OPTIONS
──────────────────────────────
PK id
FK decision_id

title
description
display_order

created_at
updated_at

EVALUATIONS
──────────────────────────────
PK id
FK option_id

criterion
score

reasoning

created_at
updated_at

RECOMMENDATIONS
──────────────────────────────
PK id
FK decision_id (UNIQUE)

selected_option_id

confidence

summary

explanation

created_at
updated_at

DOCUMENTS
──────────────────────────────
PK id
FK user_id

filename
storage_path
mime_type
file_size

created_at
updated_at

INTEGRATIONS
──────────────────────────────
PK id
FK user_id

provider

status

access_token
refresh_token

expires_at

created_at
updated_at

EMAIL_VERIFICATIONS
──────────────────────────────
PK id

FK user_id

otp_hash

expires_at

attempts

created_at

User
│
├──────────────┐
│              │
│1             │N
▼              ▼
Profile      Goals
│
│
└─────────────────────────────┐
                              │
                              ▼
                          Decisions
                     ┌────────┼────────┐
                     │        │        │
                     │1       │N       │1
                     ▼        ▼        ▼
              DecisionContext Options Recommendation
                               │
                               │N
                               ▼
                          Evaluations

User
├── Documents
└── Integrations