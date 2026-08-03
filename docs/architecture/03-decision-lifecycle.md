# Decision Lifecycle

## Purpose

Defines how every decision moves through DecisionOS from creation to completion.

---

# Lifecycle

```text
Created
    ↓
Context Collection
    ↓
Information Gathering
    ↓
Option Generation
    ↓
Evaluation
    ↓
Risk Analysis
    ↓
Recommendation
    ↓
User Decision
    ↓
Outcome Tracking
    ↓
Learning
```

---

# Stages

## 1. Created

The user submits a decision request.

**Output**

- Decision created
- Initial status assigned

---

## 2. Context Collection

DecisionOS collects all relevant information.

**Examples**

- User Profile
- Calendar
- Goals
- Constraints
- Previous Decisions

---

## 3. Information Gathering

Missing information is identified.

DecisionOS may:

- Ask follow-up questions
- Search connected integrations
- Retrieve knowledge

---

## 4. Option Generation

Possible solutions are generated.

Examples

- Accept Job
- Study Abroad
- Start Business

Every decision must contain at least one option.

---

## 5. Evaluation

Each option is analyzed.

Typical criteria

- Cost
- Time
- Career Growth
- Health
- ROI
- Family Impact

---

## 6. Risk Analysis

Potential risks are identified.

Each risk includes

- Likelihood
- Impact
- Mitigation

---

## 7. Recommendation

DecisionOS ranks the options and recommends the best one.

Includes

- Recommended Option
- Confidence
- Evidence
- Trade-offs
- Risks

---

## 8. User Decision

The user chooses to

- Accept
- Reject
- Postpone
- Request Re-evaluation

DecisionOS never silently makes high-impact decisions.

---

## 9. Outcome Tracking

DecisionOS records the real-world result.

Examples

- Accepted Offer
- Visa Rejected
- Promotion Received
- Startup Failed

---

## 10. Learning

DecisionOS improves future recommendations using

- User feedback
- Decision outcome
- Updated profile
- New evidence

---

# Decision States

| State | Description |
|--------|-------------|
| Draft | Decision created. |
| Collecting Context | Gathering required information. |
| Evaluating | Options being analyzed. |
| Recommended | Recommendation generated. |
| Waiting for User | Awaiting user action. |
| Completed | Final outcome recorded. |
| Archived | Decision closed. |

---

# State Transitions

```text
Draft
    ↓
Collecting Context
    ↓
Evaluating
    ↓
Recommended
    ↓
Waiting for User
    ↓
Completed
```

---

# Business Rules

- Every decision starts in **Draft**.
- Recommendation cannot be generated without at least one option.
- Completed decisions become read-only.
- Outcomes may update user profile and future recommendations.
- Users may reopen a completed decision for re-evaluation.
