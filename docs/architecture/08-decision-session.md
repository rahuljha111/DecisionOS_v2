# Decision Session

## Purpose

A Decision Session manages the complete lifecycle of an active decision. It coordinates user interaction, background research, context collection, and recommendation generation.

---

# Overview

```text
User Request
      │
      ▼
Create Decision
      │
      ▼
Start Decision Session
      │
      ├──────────────┐
      │              │
      ▼              ▼
Ask Questions   Background Research
      │              │
      └──────┬───────┘
             ▼
     Build Decision Context
             ▼
      Generate Options
             ▼
     Evaluate & Rank Options
             ▼
     Generate Recommendation
             ▼
        Save Outcome
```

---

# Responsibilities

- Manage decision progress
- Collect missing context
- Coordinate background research
- Build decision context
- Generate recommendations
- Track completion

---

# Session Stages

| Stage | Description |
|--------|-------------|
| Created | User submits a decision request |
| Collecting Context | Ask follow-up questions |
| Researching | Gather external information |
| Evaluating | Analyze options |
| Recommending | Generate final recommendation |
| Completed | Store result and feedback |

---

# Context Collection

DecisionOS gathers information from multiple sources.

- User Profile
- Previous Decisions
- User Responses
- Connected Integrations
- Uploaded Documents

The system only asks questions when required information is missing.

---

# Background Research

Long-running tasks execute independently from the conversation.

Examples

- University search
- Job market analysis
- Visa requirements
- Cost of living
- Scholarship search
- Health guideline lookup

Research results are attached to the active decision.

---

# User Interaction

While research is running, DecisionOS continues the conversation.

Examples

- Ask clarifying questions
- Explain why information is needed
- Update progress
- Confirm assumptions

The user should never wait without feedback.

---

# Memory Extraction

DecisionOS extracts durable information from the conversation.

Examples

Store

- Career Goal
- Preferred Country
- Budget
- IELTS Score
- Risk Preference

Ignore

- Greetings
- Small talk
- Temporary conversation

Only useful facts become part of the user's long-term profile.

---

# Recommendation

A recommendation is generated only when sufficient context is available.

The recommendation includes

- Best Option
- Supporting Evidence
- Trade-offs
- Risks
- Confidence Score

---

# Design Principles

- Research before assumptions
- Ask only relevant questions
- Prefer evidence over AI generation
- Continue interacting while processing
- Store only meaningful long-term information