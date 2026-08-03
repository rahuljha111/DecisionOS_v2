# Memory Architecture

## Purpose

Stores information required to improve future decisions.

---

## Memory Types

### User Profile

Long-term information about the user.

Examples

- Education
- Skills
- Goals
- Preferences

---

### Decision History

Stores previous decisions and outcomes.

Examples

- Decision
- Recommendation
- User Choice
- Outcome

---

### Documents

User-provided files used during decision making.

Examples

- Resume
- Offer Letter
- Medical Report

---

## Storage

All memory is stored in PostgreSQL.

Documents may also generate embeddings using pgvector for semantic search.

---

## Principles

- Keep only useful information.
- Avoid duplicate data.
- Allow updates over time.
- Keep the design simple.