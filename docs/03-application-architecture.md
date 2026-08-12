# DecisionOS v3 - Application Architecture

Version: 3.0
Status: Draft
Last Updated: 2026-08-08

---

# 1. Purpose

This document defines how DecisionOS is built.

It explains:

- application layers
- module responsibilities
- request lifecycle
- dependency direction
- interfaces
- runtime behavior

It does NOT describe:

- deployment
- Docker
- databases
- cloud infrastructure

Those belong to Infrastructure Architecture.

---

# 2. Architectural Philosophy

DecisionOS follows Clean Architecture.

The application is organized around business capabilities rather than frameworks.

Frameworks are replaceable.

Business rules are not.

Every dependency points toward the core business logic.

---

# 3. Layered Architecture

                     Frontend
                         │
                         ▼
                  API Layer (FastAPI)
                         │
                         ▼
               Application Layer
                         │
                         ▼
                  Domain Layer
                         │
                         ▼
             Infrastructure Layer

Dependencies only flow downward.

The Domain Layer never depends on Infrastructure.

---

# 4. Application Modules

DecisionOS is divided into independent modules.

## Identity

Responsibility

Authentication and authorization.

Owns

- Users
- Login
- Registration
- Sessions
- Tokens

Never owns

- Decisions
- AI
- Workflows

---

## Workflow

Responsibility

Coordinate how a decision is solved.

Owns

- Workflow execution
- State transitions
- Progress tracking

Never owns

- AI models
- Providers

---

## Agent Runtime

Responsibility

Execute specialized reasoning components.

Examples

Planner

Researcher

Critic

Scheduler

Nutrition

Career

Coding

Agents implement capabilities.

They do not contain business data.

---

## Provider Manager

Responsibility

Access AI models.

Supported providers

Gemini

Groq

Ollama

OpenRouter

Future providers

DecisionOS never calls providers directly.

Everything goes through the Provider Manager.

---

## Tool Runtime

Responsibility

Execute external tools.

Examples

Filesystem

GitHub

Calendar

Docker

Browser

Email

Database

Agents never call external APIs directly.

They request tools.

---

## Knowledge Runtime

Responsibility

Manage persistent knowledge.

Owns

- documents
- chunking
- embeddings
- retrieval

Does not manage user memory.

---

## Memory Runtime

Responsibility

Store experience.

Owns

Short-term memory

Long-term memory

Session memory

Semantic memory

Memory improves future decisions.

---

## Evaluation Runtime

Responsibility

Measure quality.

Examples

Correctness

Latency

User feedback

Cost

Quality

Evaluation improves workflows.

---

## Scheduler

Responsibility

Execute delayed work.

Examples

Nightly planning

Reminder generation

Periodic knowledge refresh

Future autonomous workflows

---

## Event Bus

Responsibility

Communication between modules.

Modules should communicate using events whenever possible.

Avoid tight coupling.

---

# 5. Request Lifecycle

A request always follows this flow.

User

↓

API

↓

Authentication

↓

Application Service

↓

Workflow

↓

Agent Runtime

↓

Provider Manager

↓

Tool Runtime

↓

Knowledge

↓

Memory

↓

Evaluation

↓

Response

Every feature should follow this lifecycle.

---

# 6. Dependency Rules

Allowed

API

↓

Application

↓

Domain

↓

Infrastructure

Forbidden

Infrastructure

↓

Domain

Forbidden

Provider

↓

Workflow

Forbidden

Tool

↓

Identity

Forbidden

Agent

↓

Database

All database access happens through repositories.

---

# 7. Interfaces

DecisionOS depends on abstractions.

Examples

LLMProvider

MemoryProvider

KnowledgeProvider

ToolProvider

WorkflowExecutor

Agent

Repository

Concrete implementations remain replaceable.

---

# 8. Plugin Architecture

DecisionOS is extensible.

Everything new should plug into an existing interface.

Examples

New AI Provider

↓

implements

LLMProvider

--------------------

New Tool

↓

implements

ToolProvider

--------------------

New Agent

↓

implements

Agent

--------------------

New Workflow

↓

implements

WorkflowExecutor

Core code should not change when new plugins are added.

---

# 9. Error Handling

Errors never leak infrastructure details.

Provider errors

↓

Application errors

↓

API responses

Users should receive meaningful messages.

Internal logs contain technical details.

---

# 10. Observability

Every workflow execution records

Request ID

Execution ID

Latency

Provider

Model

Tool usage

Token usage

Cost

Status

Errors

DecisionOS should always explain what happened.

---

# 11. AI Routing

Agents never choose models.

Agents request capabilities.

Example

Need

↓

High reasoning

↓

Provider Manager

↓

OmniRoute

↓

Gemini

or

Groq

or

Ollama

Model routing is infrastructure.

Agents remain provider agnostic.

---

# 12. Future Evolution

Future additions

Voice

Vision

GraphRAG

Multi-user collaboration

Human approval

Distributed execution

Enterprise connectors

These should integrate without changing existing modules.

---

# 13. Engineering Principle

Modules own responsibilities.

Interfaces define contracts.

Implementations remain replaceable.

Business logic remains independent from technology.notepad $PROFILE