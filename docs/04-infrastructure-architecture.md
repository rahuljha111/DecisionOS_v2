# DecisionOS v3 - Infrastructure Architecture

Version: 3.0
Status: Draft
Last Updated: 2026-08-08

---

# 1. Purpose

This document defines the infrastructure that powers DecisionOS.

It answers:

- What technologies are used?
- Why were they chosen?
- What responsibility does each component own?
- How do they interact?

Infrastructure exists to support the application.

It never contains business logic.

---

# 2. Infrastructure Philosophy

DecisionOS follows four infrastructure principles.

## Replaceable

Every infrastructure component should be replaceable.

Example

Gemini

↓

Groq

↓

Ollama

↓

Future Providers

Application code should not change.

---

## Independent

Each infrastructure service owns one responsibility.

Database stores data.

Redis caches.

OmniRoute routes models.

Docker packages services.

Responsibilities never overlap.

---

## Observable

Every request should be measurable.

Every failure should be traceable.

Every execution should be logged.

---

## Production Ready

Infrastructure should support local development today and cloud deployment tomorrow without major redesign.

---

# 3. Infrastructure Overview

                        Frontend
                            │
                            ▼
                     FastAPI Application
                            │
────────────────────────────────────────────────────

                    Core Infrastructure

────────────────────────────────────────────────────

Authentication

PostgreSQL

Redis

Object Storage

Vector Database

Knowledge Graph

OmniRoute

Logging

Monitoring

Scheduler

────────────────────────────────────────────────────

                External Integrations

────────────────────────────────────────────────────

Google Calendar

GitHub

Filesystem

Docker

Email

Browser

Weather

Search

────────────────────────────────────────────────────

                   AI Providers

────────────────────────────────────────────────────

Gemini

Groq

Ollama

OpenRouter

Future Providers

---

# 4. Infrastructure Components

## PostgreSQL

Purpose

Primary relational database.

Stores

- users
- workspaces
- goals
- decisions
- workflows
- executions
- evaluations

Reason

Reliable.

ACID compliant.

Excellent SQL support.

Strong ecosystem.

---

## Redis

Purpose

Temporary data.

Stores

- cache
- sessions
- queues
- rate limiting
- distributed locks

Redis is never the source of truth.

---

## Object Storage

Purpose

Store large files.

Examples

PDFs

Images

Audio

Videos

Documents

Generated reports

The database stores metadata.

Object storage stores files.

---

## Vector Database

Purpose

Semantic search.

Stores

Embeddings.

Supports

RAG

Semantic retrieval

Document search

Long-term knowledge retrieval

---

## Knowledge Graph

Purpose

Represent relationships.

Examples

Skill A

↓

requires

↓

Skill B

University

↓

offers

↓

Course

Graph retrieval complements vector retrieval.

It does not replace it.

---

## OmniRoute

Purpose

AI Provider Gateway.

Responsibilities

Model routing.

Fallback.

Provider abstraction.

Cost management.

DecisionOS communicates with OmniRoute.

OmniRoute communicates with providers.

---

## AI Providers

Current providers

Gemini

Groq

Ollama

Future providers can be added without modifying application code.

---

## Logging

Every request generates logs.

Logs include

Request ID

Execution ID

User

Workflow

Latency

Provider

Status

Errors

---

## Monitoring

Collects

Latency

Failures

Success rate

Token usage

Costs

Queue length

Resource utilization

Monitoring is read-only.

---

## Scheduler

Runs

Background jobs.

Examples

Knowledge indexing

Reminder generation

Memory cleanup

Document processing

Scheduled workflows

---

# 5. Data Flow

User

↓

FastAPI

↓

Application

↓

PostgreSQL

↓

Redis

↓

Vector Database

↓

Knowledge Graph

↓

OmniRoute

↓

AI Provider

↓

Application

↓

User

Infrastructure never bypasses the application.

---

# 6. Deployment Strategy

Development

Docker Compose

↓

Single Machine

↓

Local AI

↓

Hot Reload

---------------------------------

Production

Containers

↓

Reverse Proxy

↓

Database

↓

Redis

↓

Object Storage

↓

Monitoring

↓

Scaling

Deployment strategy should remain independent from business logic.

---

# 7. Security

Passwords

Argon2id

Tokens

JWT Access Token

Refresh Token

Secrets

Environment Variables

HTTPS

Required

Least Privilege

Default

Infrastructure must never expose secrets.

---

# 8. Future Infrastructure

Future additions

Neo4j Cluster

Distributed Scheduler

Kubernetes

Horizontal Scaling

Multi-region deployment

Enterprise SSO

Dedicated Embedding Service

Dedicated Model Gateway

These additions should require minimal architectural changes.

---

# 9. Engineering Principle

Infrastructure supports the application.

It should never define the application.

Technology changes.

Architecture should not.