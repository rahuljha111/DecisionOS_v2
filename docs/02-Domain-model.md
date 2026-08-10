# DecisionOS v3 - Domain Model

Version: 3.0
Status: Draft
Last Updated: 2026-08-08

---

# 1. Purpose

This document defines the core business concepts of DecisionOS.

It intentionally does **not** describe:

- FastAPI
- SQLAlchemy
- LangGraph
- Gemini
- Groq
- Ollama
- Redis
- Neo4j
- Database tables
- API endpoints

Those are implementation details.

The domain model should remain valid even if the entire technology stack changes.

---

# 2. Domain Philosophy

DecisionOS exists to help users make better decisions.

Everything in the platform supports this goal.

The domain is centered around one primary concept:

Decision

Everything else either creates, improves, executes, evaluates or remembers decisions.

---

# 3. Core Domain

## User

Represents a person using DecisionOS.

Responsibilities

- Own workspaces
- Configure preferences
- Start workflows
- Review results
- Provide feedback

A User never interacts directly with AI providers.

---

## Workspace

A logical environment owned by a user.

Purpose

Separate different contexts.

Examples

- Personal
- Career
- Startup
- Research
- University

Each workspace owns:

- Goals
- Knowledge
- Memory
- Decisions
- Workflow history

---

## Goal

Represents a long-term objective.

Examples

- Become an AI Backend Engineer
- Build DecisionOS
- Complete Master's Degree
- Improve Health

Goals give direction to decisions.

A goal may generate many decisions over time.

---

## Decision

The central business entity.

A Decision represents a problem requiring reasoning.

Examples

- Which university should I apply to?
- Should I learn GraphRAG next?
- What should I cook today?
- Which GPU should I buy?

A Decision may require:

- Planning
- Research
- Knowledge retrieval
- Memory retrieval
- Execution
- Evaluation

Everything in DecisionOS ultimately exists to improve decisions.

---

## Workflow

A reusable process used to solve a decision.

Examples

- Daily Planning
- Deep Research
- Career Planning
- Learning Roadmap
- Nutrition Planning

A workflow defines **how** a decision should be solved.

Multiple decisions may reuse the same workflow.

---

## Task

The smallest executable unit inside a workflow.

Examples

- Search documentation
- Read calendar
- Retrieve knowledge
- Generate summary
- Compare alternatives

Tasks are temporary.

They exist only while a workflow executes.

---

## Knowledge

Persistent information.

Examples

- Books
- PDFs
- Research papers
- Documentation
- Notes
- Company knowledge

Knowledge represents facts.

Knowledge is not experience.

---

## Memory

Past experiences collected by DecisionOS.

Examples

- User prefers morning study sessions.
- User dislikes tomato.
- Previous learning attempts.
- Past successful schedules.

Memory represents experience.

Memory evolves continuously.

---

## Execution

Represents one run of a workflow.

Stores

- Start time
- End time
- Status
- Outputs
- Errors
- Duration

Executions provide history.

---

## Evaluation

Measures execution quality.

Evaluation answers questions like

- Was the decision useful?
- Was the answer correct?
- Did the user accept it?
- Was execution efficient?

Evaluations improve future decisions.

---

## Artifact

Any output produced by DecisionOS.

Examples

- Research Report
- Learning Roadmap
- Daily Plan
- Architecture Document
- Recipe
- Presentation
- Checklist

Artifacts are persistent results that users can view, edit and reuse.

---

# 4. Aggregate Ownership

User

└── Workspace

Workspace

├── Goals

├── Knowledge

├── Memory

├── Decisions

├── Executions

└── Artifacts

Decision

├── Workflow

├── Tasks

├── Execution

└── Evaluation

This ownership model defines responsibility.

---

# 5. Domain Relationships

User

↓

owns

↓

Workspace

↓

contains

↓

Goals

↓

Goals create

↓

Decisions

↓

Decisions execute

↓

Workflows

↓

Workflows contain

↓

Tasks

↓

Tasks produce

↓

Artifacts

↓

Execution

↓

Evaluation

↓

Memory

Knowledge supports every workflow.

Memory improves every future decision.

---

# 6. Lifecycle

Goal

↓

Decision Created

↓

Workflow Selected

↓

Tasks Executed

↓

Knowledge Retrieved

↓

Reasoning Completed

↓

Artifact Generated

↓

Evaluation Recorded

↓

Memory Updated

↓

Decision Closed

Every decision follows this lifecycle.

---

# 7. Domain Rules

A User owns one or more Workspaces.

Every Workspace belongs to exactly one User.

A Goal belongs to one Workspace.

A Decision belongs to one Goal.

A Workflow may solve many Decisions.

A Workflow contains multiple Tasks.

Knowledge belongs to a Workspace.

Memory belongs to a Workspace.

Every Execution belongs to exactly one Decision.

Every Evaluation belongs to one Execution.

Artifacts may be reused by future Decisions.

---

# 8. Out of Scope

The domain model intentionally excludes:

- AI Agents
- AI Providers
- LLM Models
- Tools
- APIs
- Frameworks
- Databases
- Queues
- Events
- Authentication
- HTTP

Those concepts belong to the Application and Infrastructure Architecture documents.

---

# 9. Future Evolution

The domain is expected to evolve with:

- Collaboration
- Shared Workspaces
- Teams
- Organizations
- Human Approval
- Decision Templates
- Goal Dependencies
- Decision Trees

These additions should extend the model without changing its core philosophy.

---

# 10. Engineering Principle

The domain represents business concepts.

It must remain independent from implementation details.

Technology changes.

Business concepts should remain stable.