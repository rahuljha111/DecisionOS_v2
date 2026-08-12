# DecisionOS V2 — Frontend Specification

## 1. Purpose

This document is the frontend source of truth for DecisionOS V2.

The frontend must expose the backend domain model clearly and must not duplicate backend business rules. It should consume the FastAPI API through typed API clients, present domain state, manage user interaction, and provide a consistent decision-workspace experience.

The product is a decision intelligence platform. The UI should therefore feel like a structured decision workspace rather than a generic CRUD dashboard.

---

## 2. Product Principles

1. **Decision-first UX**
   - A decision is the primary unit of work.
   - Users should be able to understand what they are deciding, why, its current status, priority, alternatives, evidence, and eventual outcome.

2. **Workspace-centric navigation**
   - Workspaces provide the organizational boundary.
   - Decisions belong to workspaces.
   - The user should always understand which workspace they are operating in.

3. **Progressive complexity**
   - Basic CRUD operations must remain simple.
   - Advanced AI/research functionality should appear as capabilities around a decision rather than overwhelming the initial screen.

4. **Backend is authoritative**
   - Validation, permissions, lifecycle rules, status transitions, and business constraints belong to the backend.
   - Frontend validation is for UX only and must never be treated as security.

5. **Typed contracts**
   - API request/response models should have corresponding frontend types.
   - Avoid untyped `any`-based API handling.

6. **Consistent states**
   Every data-driven screen should explicitly handle:
   - loading
   - empty
   - success
   - validation error
   - authorization error
   - not found
   - server error

---

## 3. Recommended Frontend Stack

- React
- TypeScript
- Vite
- React Router
- A server-state/data-fetching layer such as TanStack Query
- A form solution such as React Hook Form
- Schema validation aligned with API contracts
- Centralized HTTP/API client
- Centralized authentication/session handling
- Component library/design system rather than page-specific styling

The exact library choice may evolve, but the architectural responsibilities must remain the same.

---

## 4. Frontend Architecture

Recommended structure:

```text
src/
├── app/
│   ├── router/
│   ├── providers/
│   └── config/
│
├── components/
│   ├── ui/
│   ├── forms/
│   ├── feedback/
│   └── layout/
│
├── features/
│   ├── auth/
│   ├── workspace/
│   ├── decision/
│   ├── research/
│   ├── alternatives/
│   ├── recommendation/
│   └── knowledge/
│
├── services/
│   ├── api/
│   ├── auth/
│   └── storage/
│
├── hooks/
├── types/
├── utils/
└── styles/
```

### Feature ownership

Each feature should contain its own:

- pages
- components
- hooks
- API functions
- types
- validation
- feature-specific utilities

Shared components belong in `components/`, not inside an unrelated feature.

---

## 5. Authentication / Identity UI

Identity backend work is **completed** as of the current project checkpoint.

Frontend must support:

### Public routes

- Login
- Registration
- Authentication failure handling

### Protected routes

All workspace and decision functionality must require an authenticated session.

### Session behavior

- Store tokens/session state according to the backend authentication contract.
- Automatically attach credentials to API requests.
- Handle expired/invalid authentication centrally.
- Redirect unauthenticated users to login.
- Do not scatter authentication checks across every component.

### Identity UI requirements

- Login form
- Registration form
- Loading state
- Field validation
- API error display
- Logout action
- Authenticated application shell

Do not implement authorization logic independently in the frontend. The frontend may hide unavailable actions for UX, but the backend remains the enforcement point.

---

## 6. Application Shell

Authenticated users should enter a consistent application shell.

Recommended structure:

```text
┌───────────────────────────────────────────┐
│ Top Bar                                   │
├──────────────┬────────────────────────────┤
│ Sidebar      │ Main Content               │
│              │                            │
│ Workspaces   │ Page / Feature             │
│ Decisions    │                            │
│ Settings     │                            │
└──────────────┴────────────────────────────┘
```

The shell should provide:

- current workspace context
- primary navigation
- user/account menu
- logout
- breadcrumbs where useful
- global error handling
- responsive behavior

---

## 7. Workspace Module

Workspace is the first major protected product area.

### Required functionality

- List workspaces
- Create workspace
- View workspace
- Update workspace
- Delete workspace where backend permits
- Switch active workspace
- Display workspace membership/access state

### Workspace list

Should provide:

- workspace name
- description where applicable
- ownership/access indication
- decision count where available
- create action
- open action

### Workspace detail

Should provide:

- workspace information
- edit/delete actions according to permission
- member/access information
- decisions belonging to the workspace
- create decision action

### Permissions

Frontend should represent permission-aware UI:

```text
Can view      → show workspace
Can create    → show create action
Can update    → show edit action
Can delete    → show delete action
```

These are UI affordances only. Backend authorization remains authoritative.

---

## 8. Decision Module

Decision is the core product entity.

### Decision list

Display at minimum:

- title
- status
- priority
- workspace
- created/updated information
- relevant lifecycle metadata

Provide:

- search/filtering when supported by API
- status filtering
- priority filtering
- create decision
- open decision

### Create decision

Required fields must follow the backend contract.

The form should clearly distinguish:

- required fields
- optional context
- lifecycle defaults

### Decision detail

The decision page should become the central workspace for the decision.

Recommended sections:

```text
Decision Header
├── Title
├── Status
├── Priority
├── Actions
│
├── Context / Description
│
├── Alternatives
│
├── Research / Evidence
│
├── Analysis
│
├── Recommendation
│
└── Decision Outcome / History
```

Not all sections need to be active in the MVP. They should be designed so later modules can be added without redesigning the whole page.

---

## 9. Decision Lifecycle UI

Status is a domain lifecycle concept.

Frontend must:

- display current status clearly
- show only lifecycle actions permitted by backend
- confirm destructive or irreversible transitions
- refresh state after successful transitions
- display transition errors from backend

Do not hard-code arbitrary status transitions in the frontend.

The frontend may maintain a display mapping:

```text
Backend status → UI label → UI presentation
```

but the allowed transition matrix belongs to the backend.

---

## 10. Priority UI

Priority should be represented consistently wherever decisions appear.

Examples:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The exact enum must match the backend contract.

Do not duplicate enum definitions manually in multiple files.

---

## 11. API Integration

All API access should go through a centralized API layer.

Avoid:

```text
Component → fetch(...)
Component → axios(...)
Component → business logic
```

Prefer:

```text
Component
   ↓
Feature Hook
   ↓
Feature API Function
   ↓
Central API Client
   ↓
FastAPI
```

API client responsibilities:

- base URL
- authentication
- headers
- serialization
- common error handling
- response normalization where required

Feature API functions should remain close to their domain.

---

## 12. Data Fetching

Server state should not be treated as ordinary local component state.

Use a server-state mechanism for:

- workspace lists
- workspace details
- decisions
- decision details
- memberships/permissions
- future research results
- future AI execution state

Handle:

- cache invalidation
- refetch after mutation
- optimistic updates only where safe
- stale data
- request cancellation where appropriate

---

## 13. Forms

Forms should:

- use typed request models
- validate user input before submission
- display field-level errors
- display API-level errors
- disable duplicate submissions
- show submission progress
- reset or redirect only after confirmed success

Do not put API calls directly into presentation-only components.

---

## 14. Error Handling

Standardize error presentation.

### Expected errors

- `400` / validation → show actionable field/form error
- `401` → session handling
- `403` → permission message
- `404` → resource not found
- `409` → conflict/business rule
- `5xx` → generic server failure with retry option

Never expose raw stack traces or internal backend errors to normal users.

---

## 15. UX Conventions

### Destructive actions

Use confirmation for:

- workspace deletion
- decision deletion
- irreversible lifecycle operations
- future destructive operations

### Empty states

Every list needs a useful empty state:

```text
No decisions yet.
Create your first decision to start working.
[Create Decision]
```

Avoid blank screens.

### Loading

Prefer:

- skeletons for page/list loading
- button-level loading for mutations
- no unnecessary full-page spinners

### Feedback

Use consistent:

- success feedback
- error feedback
- inline validation
- confirmation dialogs

---

## 16. Responsive Design

The frontend should work on:

- desktop
- laptop
- tablet
- mobile

Decision detail pages may prioritize desktop, but core CRUD and authentication flows must remain usable on smaller screens.

Do not create separate mobile and desktop business logic.

---

## 17. Accessibility

Minimum requirements:

- semantic HTML
- keyboard navigation
- visible focus states
- labels for form controls
- accessible dialogs
- appropriate ARIA only where needed
- sufficient contrast
- meaningful error messages

---

## 18. Testing

Frontend tests should cover:

### Unit/component

- forms
- validation
- status/priority display
- permission-aware actions
- error states

### Integration

- login flow
- workspace CRUD
- decision CRUD
- lifecycle interactions

### End-to-end

At minimum:

```text
Register/Login
    ↓
Create Workspace
    ↓
Open Workspace
    ↓
Create Decision
    ↓
View Decision
    ↓
Change allowed lifecycle state
    ↓
Logout
```

---

## 19. Frontend Conventions

### Naming

- Components: `PascalCase`
- Hooks: `useSomething`
- API functions: verb/domain based, e.g. `getWorkspace`, `createDecision`
- Types: descriptive domain names
- Files: follow one consistent project-wide convention

### Components

Keep components small and composable.

Do not create one giant `DecisionPage.tsx` containing:

- API calls
- forms
- business rules
- modal state
- data transformation
- rendering

Split by responsibility.

### State

Use:

- server-state library for server data
- local state for UI state
- context only for genuinely cross-cutting state

Do not put all application state into one global store.

### API contracts

Backend schema is the source of truth.

If an API contract changes:

1. update backend
2. update frontend type/client
3. update affected UI
4. update tests

### No duplicated business logic

Never duplicate:

- authorization rules
- lifecycle transition rules
- backend calculations
- persistence logic

---

## 20. Future AI UX

Future AI functionality should be embedded around the decision rather than presented as an unrelated chatbot.

Potential experience:

```text
Decision
   ↓
Research
   ↓
Evidence
   ↓
Alternatives
   ↓
Analysis
   ↓
Recommendation
   ↓
User Decision
   ↓
Outcome
   ↓
Learning
```

AI operations should show:

- current operation
- progress/status
- sources/evidence where applicable
- generated output
- uncertainty/limitations where applicable
- ability for user review before important state changes

AI must assist the user; it should not silently make irreversible decisions.

---

## 21. Definition of Done — Frontend Feature

A frontend feature is complete only when:

- API integration works
- loading state exists
- empty state exists where applicable
- validation exists
- backend errors are handled
- authorization-aware UI exists
- success feedback exists
- responsive behavior is acceptable
- tests cover important behavior
- no duplicated business rules were introduced
- code follows project conventions
