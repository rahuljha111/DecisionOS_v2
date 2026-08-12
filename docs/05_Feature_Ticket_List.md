# DecisionOS V2 — End-to-End Feature & Phase Ticket List

## 1. Purpose

This is the implementation roadmap and ticket index for DecisionOS V2.

It is intentionally organized by **feature and dependency**, not by calendar timeline.

AI coding agents should use this document to answer:

- What has already been completed?
- What is currently being implemented?
- What comes next?
- What does each feature need to contain?
- What is the expected end-to-end definition of done?
- Which conventions must be preserved?

Status values:

- `[x] COMPLETED`
- `[~] IN PROGRESS`
- `[ ] PLANNED`

Do not mark a feature completed because code merely exists. It is complete only when implementation, migration/refactor, tests, and relevant documentation are finished.

---

# 2. Current Project State

## Phase 1 — Foundation

### `[x]` Project / Architecture Foundation

Expected foundation:

- Clean/layered architecture
- module boundaries
- core/shared infrastructure
- configuration
- database integration
- migration system
- API/application bootstrap
- testing foundation
- development tooling
- engineering conventions

The foundation must remain stable while domain modules are added.

---

# 3. Phase 2 — Identity

## `[x]` Identity Module — COMPLETED

Identity establishes authentication and the user boundary for the rest of the platform.

### User management

- `[x]` User domain/model
- `[x]` User persistence
- `[x]` User schemas/contracts
- `[x]` User repository
- `[x]` User service/use-case logic

### Registration

- `[x]` Registration endpoint
- `[x]` Input validation
- `[x]` Password handling
- `[x]` Duplicate-user handling
- `[x]` Registration tests

### Authentication

- `[x]` Login/authentication flow
- `[x]` Password verification
- `[x]` Access-token generation
- `[x]` Refresh-token/session strategy where implemented
- `[x]` Authentication dependency/middleware
- `[x]` Authentication tests

### Security

- `[x]` Centralized security utilities
- `[x]` JWT handling
- `[x]` Protected route mechanism
- `[x]` Authentication error handling
- `[x]` Security configuration

### Identity quality gate

- `[x]` Migration verified
- `[x]` Tests passing
- `[x]` Architecture reviewed/refactored where necessary
- `[x]` Documentation/devlog updated

**Important:** Identity is the current completed domain baseline. Do not rebuild it while implementing Workspace unless a concrete defect or architectural inconsistency is discovered.

---

# 4. Phase 3 — Workspace + Decision

This is the next implementation phase.

---

## `[ ]` Workspace Module

### Workspace domain

- `[ ]` Workspace model
- `[ ]` Workspace schema/contracts
- `[ ]` Workspace repository
- `[ ]` Workspace service/use cases
- `[ ]` Workspace API/router/controller
- `[ ]` Workspace migration

### Workspace CRUD

- `[ ]` Create workspace
- `[ ]` Get workspace
- `[ ]` List workspaces
- `[ ]` Update workspace
- `[ ]` Delete/archive workspace according to final domain decision

### Workspace ownership/access

- `[ ]` Associate workspace with creator/owner
- `[ ]` Establish workspace access boundary
- `[ ]` Define membership/access model
- `[ ]` Enforce access at application/domain boundary
- `[ ]` Prevent cross-workspace resource access

### Workspace permissions

- `[ ]` Define workspace permissions
- `[ ]` Read permission
- `[ ]` Create permission
- `[ ]` Update permission
- `[ ]` Delete/manage permission
- `[ ]` Backend authorization enforcement
- `[ ]` Permission-aware API behavior

### Workspace tests

- `[ ]` CRUD tests
- `[ ]` Validation tests
- `[ ]` Not-found tests
- `[ ]` Duplicate/conflict tests where applicable
- `[ ]` Authorization tests
- `[ ]` Cross-workspace isolation tests

### Workspace completion gate

- `[ ]` Migration runs cleanly
- `[ ]` CRUD works end-to-end
- `[ ]` Permissions are enforced server-side
- `[ ]` Tests pass
- `[ ]` Existing Identity behavior remains intact
- `[ ]` Documentation/devlog updated

---

## `[ ]` Decision Module

Decision is the core product entity.

### Decision domain

- `[ ]` Decision model
- `[ ]` Decision schema/contracts
- `[ ]` Decision repository
- `[ ]` Decision service/use cases
- `[ ]` Decision API/router/controller
- `[ ]` Decision migration

### Decision CRUD

- `[ ]` Create decision
- `[ ]` Get decision
- `[ ]` List decisions
- `[ ]` Update decision
- `[ ]` Delete/archive decision according to final domain decision

### Workspace relationship

- `[ ]` Decision belongs to Workspace
- `[ ]` Enforce workspace isolation
- `[ ]` Prevent access to decisions outside permitted workspace
- `[ ]` Validate workspace existence/access during creation

### Decision lifecycle

Define and implement an explicit lifecycle.

The backend must own:

- valid statuses
- valid transitions
- transition validation
- transition authorization
- transition persistence

Frontend only presents the lifecycle.

Expected lifecycle concept:

```text
Draft
  ↓
Active / In Progress
  ↓
Under Review
  ↓
Decided
  ↓
Completed / Archived
```

The exact enum and transition matrix must remain centralized and should be finalized from the domain model before implementation.

### Decision status

- `[ ]` Status enum
- `[ ]` Default status
- `[ ]` Status update operation
- `[ ]` Valid transition rules
- `[ ]` Invalid transition handling
- `[ ]` Status tests

### Decision priority

- `[ ]` Priority enum
- `[ ]` Default priority if applicable
- `[ ]` Priority update
- `[ ]` Priority filtering
- `[ ]` Priority validation
- `[ ]` Priority tests

### Decision tests

- `[ ]` CRUD tests
- `[ ]` Workspace isolation tests
- `[ ]` Status tests
- `[ ]` Lifecycle transition tests
- `[ ]` Priority tests
- `[ ]` Authorization tests
- `[ ]` Validation tests

### Decision completion gate

- `[ ]` Migration clean
- `[ ]` CRUD complete
- `[ ]` Workspace relationship correct
- `[ ]` Lifecycle enforced
- `[ ]` Status/priority complete
- `[ ]` Authorization enforced
- `[ ]` Tests pass
- `[ ]` Documentation/devlog updated

---

# 5. Phase 4 — Decision Context

After Workspace + Decision foundations are stable, build the information required to make a decision.

## `[ ]` Decision Context

Potential domain capabilities:

- `[ ]` Decision goals
- `[ ]` Decision constraints
- `[ ]` Decision criteria
- `[ ]` Decision assumptions
- `[ ]` Decision stakeholders
- `[ ]` Decision deadlines/target dates where required
- `[ ]` Decision notes/context

Each capability must be evaluated as a real domain requirement before implementation. Do not create entities merely because they sound useful.

---

# 6. Phase 5 — Alternatives

## `[ ]` Alternative Management

- `[ ]` Alternative model
- `[ ]` Alternative CRUD
- `[ ]` Attach alternatives to decision
- `[ ]` Reorder alternatives
- `[ ]` Alternative attributes
- `[ ]` Alternative comparison data
- `[ ]` Alternative validation
- `[ ]` Authorization/isolation
- `[ ]` Tests

The decision should be able to answer:

```text
What are the available choices?
Why is each choice being considered?
How do the choices compare?
```

---

# 7. Phase 6 — Research & Evidence

## `[ ]` Research Module

- `[ ]` Research request model
- `[ ]` Research execution lifecycle
- `[ ]` Research job/status handling
- `[ ]` Source collection
- `[ ]` Source metadata
- `[ ]` Evidence extraction
- `[ ]` Evidence linked to decision
- `[ ]` Evidence linked to alternative/criterion where appropriate
- `[ ]` Research result persistence
- `[ ]` Failure/retry handling
- `[ ]` Tests

AI/research execution must be asynchronous where execution may be long-running.

---

# 8. Phase 7 — Analysis

## `[ ]` Decision Analysis

- `[ ]` Criteria-based evaluation
- `[ ]` Alternative scoring
- `[ ]` Weighting where justified
- `[ ]` Evidence-to-criterion linkage
- `[ ]` Analysis result persistence
- `[ ]` Explainability
- `[ ]` Analysis validation
- `[ ]` Tests

Do not hide deterministic business calculations inside an LLM prompt when they can be represented explicitly in domain logic.

---

# 9. Phase 8 — AI Decision Engine

## `[ ]` AI Orchestration

DecisionOS should remain model-agnostic.

Architecture:

```text
DecisionOS
    ↓
AI Application / Orchestration Layer
    ↓
Provider Abstraction
    ↓
Gemini / Groq / Ollama / OpenRouter / Future Providers
```

### Provider abstraction

- `[ ]` Provider interface
- `[ ]` Provider configuration
- `[ ]` Model selection
- `[ ]` Timeout handling
- `[ ]` Retry handling
- `[ ]` Failure handling
- `[ ]` Usage/metadata capture

### Agent/workflow orchestration

- `[ ]` Research agent/workflow
- `[ ]` Analysis agent/workflow
- `[ ]` Alternative evaluation
- `[ ]` Recommendation generation
- `[ ]` Structured outputs
- `[ ]` Agent execution state
- `[ ]` Persist important outputs
- `[ ]` Traceability

### AI safety/product behavior

- `[ ]` User review before consequential actions
- `[ ]` Source/evidence visibility
- `[ ]` Uncertainty/limitations
- `[ ]` No silent irreversible decisions
- `[ ]` Failure recovery
- `[ ]` Auditability

---

# 10. Phase 9 — Recommendation

## `[ ]` Recommendation Module

- `[ ]` Recommendation model
- `[ ]` Recommendation generation
- `[ ]` Recommendation linked to decision
- `[ ]` Supporting evidence
- `[ ]` Rationale
- `[ ]` Confidence/uncertainty where meaningful
- `[ ]` User review
- `[ ]` Accept/reject/refine workflow
- `[ ]` Tests

A recommendation is an output of analysis, not a replacement for the user's decision.

---

# 11. Phase 10 — Decision Outcome & Learning

## `[ ]` Decision Outcome

- `[ ]` Record final decision
- `[ ]` Record selected alternative
- `[ ]` Record rationale
- `[ ]` Record outcome
- `[ ]` Record actual result
- `[ ]` Compare expected vs actual outcome
- `[ ]` Outcome history
- `[ ]` Tests

## `[ ]` Learning Layer

- `[ ]` Historical decision retrieval
- `[ ]` Outcome-based learning signals
- `[ ]` Decision pattern extraction
- `[ ]` User/project knowledge
- `[ ]` Reusable evidence/knowledge
- `[ ]` Feedback loops

Learning must be based on persisted decision data and outcomes, not vague "AI memory".

---

# 12. Phase 11 — Platform Capabilities

Implement only when justified by actual product requirements.

## `[ ]` Audit

- `[ ]` Important domain event logging
- `[ ]` Authentication/security events
- `[ ]` Permission changes
- `[ ]` Decision lifecycle changes
- `[ ]` AI execution trace where appropriate

## `[ ]` Notifications

- `[ ]` Notification model
- `[ ]` In-app notifications
- `[ ]` Async notification processing
- `[ ]` User preferences

## `[ ]` Search

- `[ ]` Workspace search
- `[ ]` Decision search
- `[ ]` Evidence/source search
- `[ ]` Future semantic search

## `[ ]` Observability

- `[ ]` Structured logging
- `[ ]` Request correlation
- `[ ]` Metrics
- `[ ]` AI execution monitoring
- `[ ]` Error tracking

---

# 13. End-to-End Feature Implementation Contract

Every feature must follow this sequence.

```text
1. Understand existing architecture
        ↓
2. Inspect analogous modules
        ↓
3. Define domain behavior
        ↓
4. Define database/model changes
        ↓
5. Create/update migration
        ↓
6. Implement repository/data access
        ↓
7. Implement application/service logic
        ↓
8. Implement API schemas
        ↓
9. Implement router/controller/API endpoint
        ↓
10. Implement authorization
        ↓
11. Add tests
        ↓
12. Run migrations
        ↓
13. Run full relevant test suite
        ↓
14. Refactor for project conventions
        ↓
15. Update documentation/devlog
        ↓
16. Mark ticket COMPLETED
```

Do not skip layers because a feature appears small.

---

# 14. Backend Conventions

## Architecture

Use:

```text
Router/API
    ↓
Application / Service
    ↓
Domain
    ↓
Repository / Infrastructure
    ↓
Database
```

Dependency direction must remain inward.

Domain logic must not depend directly on:

- FastAPI
- SQLAlchemy implementation details
- database sessions
- provider SDKs

---

## Module boundaries

Each domain module should own its:

- model
- schema
- repository
- service/use cases
- API layer
- tests

Cross-module communication should happen through explicit interfaces/use cases rather than reaching directly into another module's internals.

---

## Database

- PostgreSQL is the database.
- All schema changes require migrations.
- Never modify production schema manually.
- Migration files must be deterministic and reviewable.
- Do not create duplicate/competing migrations for the same change.
- Verify both upgrade and downgrade behavior where appropriate.

---

## Repository

Use the established repository abstraction.

Repositories handle persistence concerns.

Repositories should not become a dumping ground for domain business rules.

---

## Transactions

Transaction boundaries should be explicit.

A service/use case should own a coherent business operation rather than scattering transaction management across unrelated repository methods.

---

## Validation

Pydantic/API validation handles input shape.

Domain/application logic handles business validity.

Database constraints enforce persistence invariants.

Do not rely on only one layer.

---

## Authorization

Authorization must be enforced server-side.

For workspace-scoped resources:

```text
Authenticated User
       ↓
Workspace Access
       ↓
Resource Access
```

Never trust a workspace/resource ID supplied by the client without verifying ownership or permission.

---

## Enums

Domain enums must have one authoritative definition.

Do not duplicate status/priority values across:

- models
- schemas
- services
- frontend

The API contract should expose the authoritative values.

---

## Async work

Long-running AI/research operations should not block normal request/response cycles.

Use the project's established background-job infrastructure where appropriate.

Persist job/execution state so clients can observe progress.

---

# 15. Testing Conventions

Every feature must have tests at the appropriate levels.

Minimum expectations:

- happy path
- validation failure
- not found
- authorization failure
- cross-tenant/workspace access failure where applicable
- business-rule failure
- persistence behavior
- lifecycle transitions where applicable

A green test suite is necessary but not sufficient. Tests must exercise the actual domain behavior.

---

# 16. Migration Conventions

Before declaring a database feature complete:

```text
Create migration
    ↓
Run upgrade
    ↓
Verify schema
    ↓
Run tests
    ↓
Verify application startup
```

If migration history is inconsistent, fix the migration history instead of bypassing Alembic.

Never casually delete or rewrite historical migrations that may already be part of the shared project history.

---

# 17. AI Coding Agent Instructions

Before changing code, an AI agent must:

1. Read the architecture documentation.
2. Inspect the target module.
3. Inspect at least one analogous completed module.
4. Identify existing conventions.
5. Check migration history.
6. Check existing tests.
7. Make the smallest coherent change.
8. Reuse existing abstractions instead of inventing parallel ones.

After changing code:

1. Run formatting/linting if configured.
2. Run relevant tests.
3. Run broader tests when practical.
4. Run/check migrations.
5. Inspect the final diff.
6. Remove accidental changes.
7. Update documentation/devlog.
8. Report exactly what was completed and what remains.

Do not:

- rewrite unrelated modules
- introduce a second architectural pattern
- duplicate infrastructure
- silently change API contracts
- bypass authorization
- mark incomplete work as complete
- add speculative abstractions without a concrete requirement

---

# 18. Completion Rules

A phase is complete only when all required tickets in that phase are complete.

A ticket is complete only when:

```text
Implementation
+ Migration
+ Validation
+ Authorization
+ Tests
+ Refactor
+ Documentation
= COMPLETED
```

If one of these is intentionally not applicable, document why.

---

# 19. Current Execution Pointer

The project should currently continue from:

```text
[x] Foundation
[x] Identity

→ NEXT

[ ] Workspace
[ ] Decision
```

Do not jump to AI orchestration before the core domain model is stable.

The correct dependency order is:

```text
Identity
   ↓
Workspace
   ↓
Decision
   ↓
Decision Context
   ↓
Alternatives
   ↓
Research / Evidence
   ↓
Analysis
   ↓
AI Orchestration
   ↓
Recommendation
   ↓
Outcome
   ↓
Learning
```

This order is intentional: AI capabilities depend on a stable decision domain. Building the agent layer before the domain model would create unnecessary coupling and rework.
