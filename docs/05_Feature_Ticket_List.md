Phase 1 — Platform Foundation

Status: ✅ Complete

Objective

Build a stable production-oriented backend foundation before implementing business and AI capabilities.

Core Infrastructure
 Project architecture
 Configuration management
 Environment management
 API aggregation
 Async SQLAlchemy
 PostgreSQL
 Alembic
 Base model
 UUID infrastructure
 Timestamp infrastructure
 BaseRepository
 Dependency injection
Security Foundation
 Argon2 password hashing
 JWT authentication
 Current-user dependency
 Authentication flow
 Security middleware
Platform Middleware
 Request ID
 Structured logging
 CORS
 Trusted hosts
 Rate limiting
 Global exception handling
 Domain exceptions
 Production-safe errors
Health
 /live
 /ready
 /health
Completion Gate
 Architecture established
 Database operational
 Migrations operational
 Authentication infrastructure operational
 Middleware operational
 Error handling operational
 Tests passing
 Documentation updated
Phase 2 — Identity

Status: ✅ Complete

Objective

Implement the user identity and authentication domain.

Identity
 User model
 User registration
 Login
 Password hashing
 Password verification
 JWT generation
 JWT verification
 Current-user endpoint
 Identity repository
 Identity service
 Identity router
 Authentication dependencies
Architecture
Router
   ↓
Service
   ↓
Repository
   ↓
Database
Completion Gate
 Migration clean
 CRUD/authentication complete
 JWT flow verified
 Authorization foundation established
 Tests pass
 Documentation/devlog updated

Identity is now the reference implementation for future modules.

Phase 3 — Workspace + Decision

Status: ✅ Complete

Objective

Establish the first real DecisionOS business domain.

Workspace

Workspace is the primary organizational and authorization boundary.

User
  ↓
Workspace
Workspace Capabilities
 Workspace model
 Workspace CRUD
 Workspace ownership
 Workspace access control
 Workspace authorization
 Permission foundation
 Workspace repository
 Workspace service
 Workspace router
 Tests
Decision

A Decision represents a problem/question requiring a choice.

Workspace
    ↓
Decision
Decision Capabilities
 Decision model
 Decision CRUD
 Workspace relationship
 Workspace-scoped authorization
 Decision status
 Decision priority
 Decision lifecycle
 Decision repository
 Decision service
 Decision router
 Tests
Decision Lifecycle
DRAFT
  ↓
ACTIVE
  ↓
UNDER_REVIEW
  ↓
DECIDED
  ↓
COMPLETED
Priority
LOW
MEDIUM
HIGH
CRITICAL

Default:

MEDIUM
Completion Gate
 Migration clean
 CRUD complete
 Workspace relationship correct
 Lifecycle enforced
 Status/priority complete
 Authorization enforced
 Tests pass
 Documentation/devlog updated
Phase 4 — Knowledge & Ingestion Platform

Status: ⬜ Planned

Objective

Build the information acquisition and ingestion layer that provides DecisionOS with high-quality knowledge from user-provided and external sources.

Knowledge belongs to the Workspace.

Workspace
   ↓
Knowledge
   ├── User Documents
   └── Web Sources

The objective is not simply file upload.

It is:

Acquire
  ↓
Extract
  ↓
Normalize
  ↓
Validate
  ↓
Chunk
  ↓
Embed
  ↓
Index
4.1 Document Upload

Support initial formats:

 PDF
 Images
 Markdown
 TXT
 DOCX where appropriate

Future formats should be added only when justified.

4.2 Document Processing
Document
   ↓
Parser
   ↓
Text Extraction
   ↓
OCR if required
   ↓
Normalization
   ↓
Quality Validation

Capabilities:

 PDF text extraction
 Image processing
 OCR
 Text normalization
 Metadata extraction
 Content validation
 Processing status
 Failure handling
4.3 Web Knowledge Ingestion

DecisionOS must eventually be able to acquire knowledge without requiring users to upload documents.

Decision
   ↓
Search Query
   ↓
Web Search Provider
   ↓
Candidate Sources
   ↓
Content Extraction
   ↓
Quality Validation
   ↓
Knowledge

Store source provenance:

 URL
 Title
 Domain
 Publication date where available
 Retrieval timestamp
 Search query
 Source type
 Content hash
 Provider metadata

Do not store another LLM's generated answer as authoritative knowledge.

Store the underlying source content and provenance.

4.4 Quality Gates

Knowledge should not blindly accept every source.

Implement deterministic quality checks such as:

 Valid source
 Successful extraction
 Meaningful content
 Minimum content threshold
 Duplicate detection
 Boilerplate/spam filtering
 Relevance metadata
 Content hashing

The system should be able to:

ACCEPT
REJECT

sources based on explicit rules.

4.5 Chunking
Document
   ↓
Normalized Text
   ↓
Chunks

Chunk metadata should preserve:

 document_id
 chunk_id
 chunk_index
 page number where available
 section information where available
 source metadata

Chunking should be implemented behind a reusable abstraction.

4.6 Embeddings

Create an embedding abstraction:

EmbeddingProvider
        ↓
Concrete Provider

Requirements:

 Provider abstraction
 Configurable model
 Configurable dimensions where supported
 Error handling
 Retry handling
 Metadata capture

Do not hard-code embedding provider calls throughout business services.

4.7 Storage Architecture

Freeze the storage boundaries now.

PostgreSQL
    ↓
Application metadata/state

Object Storage
    ↓
Original files

Qdrant
    ↓
Vector embeddings

Redis
    ↓
Task broker

TaskIQ
    ↓
Background ingestion

Use an object-storage abstraction so development storage can later move to S3/GCS/S3-compatible infrastructure without rewriting Knowledge.

4.8 Async Ingestion

Long-running processing must not block HTTP requests.

Upload
   ↓
Document = QUEUED
   ↓
TaskIQ
   ↓
Redis
   ↓
Worker
   ↓
Process
   ↓
READY

Document lifecycle:

UPLOADED
   ↓
QUEUED
   ↓
PROCESSING
   ↓
READY

Failure:

PROCESSING
   ↓
FAILED

Implement:

 TaskIQ
 Redis
 Retry handling
 Job failure handling
 Idempotency
 Processing status
 Recovery strategy
4.9 Deduplication

Use content hashing.

File
  ↓
SHA-256
  ↓
content_hash

Avoid indexing identical content repeatedly.

For web content, use appropriate URL/content hashing.

4.10 Qdrant

Use Qdrant as the vector retrieval store.

Do not create one collection per user/workspace.

Use a shared collection with payload metadata such as:

 workspace_id
 document_id
 chunk_id
 source_type
 content_hash
 metadata

Workspace isolation must be enforced during vector search.

4.11 Authorization

Every Knowledge operation must follow:

JWT
 ↓
Principal
 ↓
Workspace Access
 ↓
Knowledge Resource
 ↓
Operation

Search must never retrieve information outside the user's authorized Workspace.

Tests

Create tests under:

tests/knowledge/

Cover:

 Upload
 Validation
 Authorization
 Document lifecycle
 Processing failures
 Chunking
 Deduplication
 Embedding failures
 Web ingestion
 Workspace isolation
 Qdrant integration where appropriate
 Async job behavior
Database

Create and review all required Alembic migrations.

Do not modify existing migration history destructively.

Completion Gate
 Upload complete
 File storage complete
 PDF/image processing complete
 OCR complete where required
 Web ingestion complete
 Quality gates implemented
 Chunking complete
 Embeddings complete
 Qdrant integrated
 TaskIQ integrated
 Redis integrated
 Object storage abstraction integrated
 Workspace authorization enforced
 Deduplication implemented
 Retries/idempotency implemented
 Migrations verified
 Tests pass
 Documentation/devlog updated
Phase 5 — RAG Platform

Status: ⬜ Planned

Objective

Turn stored Knowledge into relevant context for AI systems.

Knowledge
   ↓
Retrieval
   ↓
Context
   ↓
Prompt
5.1 Retrieval

Implement:

 Semantic search
 Workspace filtering
 Top-K
 Score threshold
 Document filtering
 Source filtering
 Metadata filtering

Architecture:

Query
  ↓
Embedding
  ↓
Qdrant
  ↓
Relevant Chunks
5.2 Retrieval Evolution

Design for future support:

Dense Retrieval
      ↓
Hybrid Retrieval
      ↓
Reranking

Potential future capabilities:

 Dense retrieval
 Sparse/BM25 retrieval
 Hybrid retrieval
 Reranking
 Retrieval fusion

Do not implement unnecessary retrieval complexity until justified.

Phase 6 — Context & Prompt Engineering

Status: ⬜ Planned

Objective

Convert retrieved information into high-quality, bounded model context.

6.1 Context Builder
Retrieved Chunks
      ↓
Deduplication
      ↓
Ranking
      ↓
Token Budget
      ↓
Context

Implement:

 Context assembly
 Source metadata
 Token budgeting
 Chunk ordering
 Duplicate removal
 Context compression where justified
6.2 Prompt Pipeline
Prompt Template
      ↓
Prompt Builder
      ↓
Context
      ↓
User Request
      ↓
Final Prompt

Implement:

 Prompt templates
 Prompt versioning
 System instructions
 Context injection
 Structured output requirements
 Prompt validation

Prompts should not be hard-coded inside routers.

Phase 7 — Decision Context & Alternatives

Status: ⬜ Planned

Objective

Expand the Decision domain only where real product requirements justify additional concepts.

Decision Context

Potential capabilities:

 Goals
 Constraints
 Criteria
 Assumptions
 Stakeholders
 Deadlines/target dates
 Notes/context

Every entity must be justified as a real domain requirement.

Do not create entities merely because they sound useful.

Alternatives
Decision
   ├── Alternative A
   ├── Alternative B
   └── Alternative C

Implement:

 Alternative model
 Alternative CRUD
 Attach alternatives to Decision
 Reorder alternatives
 Alternative attributes
 Comparison data
 Validation
 Authorization/isolation
 Tests

The Decision domain should be able to answer:

What choices are available?
Why are they being considered?
How do they compare?
Phase 8 — AI Runtime

Status: ⬜ Planned

Objective

Create a model-agnostic LLM runtime.

Architecture:

DecisionOS
    ↓
AI Runtime
    ↓
Provider Abstraction
    ↓
┌──────────┬──────────┬──────────┬──────────┐
│ Gemini   │ Groq     │ Ollama   │ OmniRoute│
└──────────┴──────────┴──────────┴──────────┘
Provider Abstraction
 Provider interface
 Provider configuration
 Model selection
 Timeout handling
 Retry handling
 Failure handling
 Structured outputs
 Usage metadata
 Token metadata
Providers
 Gemini
 Groq
 Ollama
 OmniRoute

Providers must implement the same application-facing abstraction.

The business domain must not depend directly on provider SDKs.

Model Routing

Future capability:

Task
 ↓
Model Router
 ├── Fast/Cheap Model
 ├── Reasoning Model
 └── Local Model
Streaming
 Streaming abstraction
 API streaming
 Cancellation
 Failure handling
Phase 9 — Agent Runtime

Status: ⬜ Planned

Objective

Introduce stateful AI workflows after the Knowledge, RAG, and AI Runtime layers are stable.

Use LangGraph.

State
 ↓
Node
 ↓
Edge
 ↓
Checkpoint
 ↓
Execution
Agent Runtime
 LangGraph integration
 State model
 Node abstraction
 Edge/transition handling
 Checkpointing
 Execution lifecycle
 Failure recovery
 Tool execution
Supervisor
                 Supervisor
                /    |     \
               /     |      \
        Research   Analysis  Evaluation

Implement:

 Supervisor workflow
 Agent routing
 State propagation
 Failure handling
Execution State

Persist meaningful execution state:

 Agent run
 Current node
 Inputs
 Outputs
 Errors
 Timestamps
 Execution status

Do not introduce long-term user memory here.

Phase 10 — Deep Research Engine

Status: ⬜ Planned

Objective

Build an autonomous but controlled research workflow for Decisions.

Decision
   ↓
Planner
   ↓
Researcher
   ↓
Sources
   ↓
Evidence
   ↓
Critic
   ↓
More Research?
   │
   ├── YES
   │
   └── NO
        ↓
    Synthesizer
        ↓
    Research Report
Planner
 Research question decomposition
 Search strategy
 Research objectives
 Research state
Researcher
 Search execution
 Source retrieval
 Source ingestion
 Evidence extraction
 Source metadata
Critic

Evaluate:

 Weak sources
 Missing evidence
 Contradictions
 Unsupported claims
 Research completeness
Synthesizer
 Structured research report
 Source references
 Evidence traceability
 Uncertainty
 Research conclusion

Long-running research must execute asynchronously.

Phase 11 — Decision Intelligence

Status: ⬜ Planned

Objective

Transform research, evidence, criteria, and alternatives into structured decision analysis.

Deterministic Analysis
Criteria
   ↓
Weights
   ↓
Alternative Scores
   ↓
Calculated Result

Implement:

 Criteria evaluation
 Alternative scoring
 Weighting where justified
 Deterministic calculations
 Validation

Do not hide deterministic business calculations inside LLM prompts.

Evidence Analysis
 Evidence-to-criterion linkage
 Evidence-to-alternative linkage
 Evidence quality
 Conflicting evidence
 Explainability
AI Analysis
Research
+
Evidence
+
Criteria
+
Alternatives
+
User Context
      ↓
AI Analysis

AI may analyze:

 Tradeoffs
 Risks
 Contradictions
 Missing information
 Qualitative considerations
Recommendation
Analysis
   ↓
Recommendation

Implement:

 Recommendation model
 Recommendation generation
 Supporting evidence
 Rationale
 Confidence/uncertainty
 User review
 Accept/reject/refine

A recommendation is not a replacement for the user's decision.

Phase 12 — Memory & Knowledge Graph

Status: ⬜ Planned

Objective

Build structured long-term knowledge from conversations, decisions, outcomes, and entities.

Conversation Memory
Conversation
   ↓
Messages
   ↓
Short-term Context

Implement:

 Conversation model
 Message history
 Context management
 Conversation summarization where justified
Long-Term Memory

Persist only meaningful durable information.

Potential categories:

 User preferences
 Decision history
 Important constraints
 Past outcomes
 Repeated patterns

Do not turn every conversation message into memory.

Knowledge Graph

Use Neo4j where relationships provide meaningful value.

Potential entities:

User
 ↓
Workspace
 ↓
Decision
 ↓
Alternative
 ↓
Criterion
 ↓
Evidence
 ↓
Entity

Implement:

 Neo4j integration
 Entity extraction
 Entity persistence
 Relationship persistence
 Graph queries
 Graph synchronization
Phase 13 — GraphRAG

Status: ⬜ Planned

Objective

Combine semantic retrieval with structured graph reasoning.

Architecture:

Query
 │
 ├───────────────┐
 ▼               ▼
Qdrant          Neo4j
 │               │
Semantic        Relationships
Retrieval       Traversal
 │               │
 └───────┬───────┘
         ▼
       Fusion
         ↓
      Reranking
         ↓
      Context
         ↓
        LLM

Implement:

 Vector retrieval
 Graph traversal
 Relationship-aware retrieval
 Retrieval fusion
 Reranking
 Graph/vector context assembly
 Tests
Phase 14 — Productivity Integrations

Status: ⬜ Planned

Objective

Connect DecisionOS with external user productivity systems.

Google OAuth
 Google OAuth
 Token management
 Scope management
 Secure credential storage
 Token refresh
 Revocation handling
Gmail

Potential capabilities:

 Search email
 Retrieve relevant messages
 Extract evidence
 Attach evidence to Decisions
Calendar

Potential capabilities:

 Read events
 Create events
 Decision deadlines
 Scheduling
 Reminders

Consequential external actions require explicit user confirmation.

Phase 15 — Multimodal DecisionOS

Status: ⬜ Planned

Objective

Allow DecisionOS to understand visual and voice-based information.

Vision
Image
 ↓
Vision Model
 ↓
Structured Understanding
 ↓
Knowledge

Potential capabilities:

 Image analysis
 Charts
 Screenshots
 Tables
 Diagrams
 Visual evidence
 Document understanding

OCR remains one processing capability within the larger vision system.

Voice

Architecture:

Microphone
   ↓
LiveKit / Pipecat
   ↓
Speech-to-Text
   ↓
DecisionOS
   ↓
LLM
   ↓
Text-to-Speech
   ↓
User

Implement:

 LiveKit/Pipecat integration
 Streaming
 Speech-to-text
 Text-to-speech
 Turn detection
 Interruptions
 Cancellation
 Low-latency execution
Phase 16 — AI Evaluation & Observability

Status: ⬜ Planned

Objective

Measure AI quality instead of assuming the AI works correctly.

AI Observability

Track:

Request
   ↓
Retrieval
   ↓
Prompt
   ↓
Model
   ↓
Output

Capture:

 Latency
 Token usage
 Model
 Provider
 Retrieval scores
 Source IDs
 Failures
 Retries
 Cost metadata
RAG Evaluation

Create evaluation datasets and measure:

 Retrieval recall
 Retrieval precision
 Context relevance
 Faithfulness
 Answer relevance
Agent Evaluation

Measure:

 Task success
 Tool selection
 Execution failures
 Loops
 Latency
 Cost
Traceability

Every important AI operation should be traceable through:

Request
 ↓
Agent/Workflow
 ↓
Retrieval
 ↓
Sources
 ↓
Prompt
 ↓
Model
 ↓
Output
Phase 17 — Production Engineering

Status: ⬜ Planned

Objective

Prepare DecisionOS for reliable production deployment.

Containerization
 Docker
 Production configuration
 Service configuration
 Environment separation
 Database migration execution
CI/CD
Git Push
   ↓
Tests
   ↓
Lint
   ↓
Type Check
   ↓
Build
   ↓
Deploy

Implement:

 CI pipeline
 Automated tests
 Linting
 Type checking
 Build verification
 Deployment pipeline
Observability
 Structured logs
 Metrics
 Request correlation
 Distributed tracing
 Error tracking
 AI execution monitoring
 Infrastructure monitoring
Reliability
 Timeouts
 Retries
 Idempotency
 Job recovery
 Graceful degradation
 Failure isolation
 Backups
 Recovery procedures
Security
 Secret management
 Production CORS
 Trusted hosts
 Rate limiting
 Authorization review
 Dependency auditing
 Secure file handling
 External integration security
Architecture Evolution

DecisionOS should evolve through the following layers:

                    DecisionOS
                        │
        ┌───────────────┴────────────────┐
        │                                │
   BUSINESS DOMAIN                    AI SYSTEM
        │                                │
        ▼                                ▼
 User → Workspace → Decision        Knowledge
                                      │
                                      ▼
                                     RAG
                                      │
                                      ▼
                                 AI Runtime
                                      │
                                      ▼
                                 Agent Runtime
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                    Research                  Analysis
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                                Recommendation
                                      │
                                      ▼
                                   Outcome
                                      │
                                      ▼
                                  Learning

Underlying infrastructure:

┌─────────────────────────────────────────────────────────┐
│ Platform Infrastructure                                 │
│                                                         │
│ PostgreSQL | Redis | TaskIQ | Qdrant | Object Storage  │
│ Neo4j | Observability | Docker | CI/CD                 │
└─────────────────────────────────────────────────────────┘
Technology Strategy

Technologies should be used because they solve concrete problems.

Technology	Purpose
PostgreSQL	Primary application database
Redis	Task broker/cache infrastructure
TaskIQ	Background/long-running jobs
Qdrant	Vector retrieval
Object Storage	Original files
OCR	Document/image text extraction
Gemini	General/reasoning/multimodal LLM
Groq	Low-latency inference
Ollama	Local/private inference
OmniRoute	Unified model routing/experimentation
LangGraph	Stateful agent workflows
Neo4j	Entity/relationship graph
GraphRAG	Graph + vector retrieval
LiveKit/Pipecat	Real-time voice
Evaluation Layer	AI quality measurement
Docker	Containerization
CI/CD	Automated delivery

Do not add technology solely to increase the technology count.

Every component must have:

A clear problem it solves.
A defined architectural boundary.
Tests.
Configuration.
Failure handling where applicable.
Documentation.
Global Engineering Rules

Every new module must follow:

Router
   ↓
Service
   ↓
Repository
   ↓
Database

Where appropriate, additional infrastructure components may exist behind services through explicit interfaces.

Dependency Direction
Business Modules
      ↓
Core / Infrastructure

Core must not depend on business modules.

Testing

Every phase must add relevant tests under:

tests/<module>/

Do not consider a feature complete without tests.

Testing should include:

Happy paths
Validation failures
Authorization failures
Not found cases
Business-rule violations
Integration behavior
Failure/retry behavior where applicable
Database

Every schema change requires:

 Alembic migration
 Migration review
 Upgrade verification
 Downgrade consideration where appropriate
 No destructive migration-history rewriting
Security

Every resource must be evaluated for:

Authentication
Authorization
Workspace isolation
Input validation
File security
Secret handling
External integration security
Async Work

Any operation that may become long-running should not block HTTP requests.

Examples:

Document ingestion
OCR
Embedding generation
Web research
Agent workflows
Large AI operations
External integration jobs

Use the background-job infrastructure where appropriate.

AI Provider Independence

Business logic must never directly depend on:

Gemini SDK
Groq SDK
OpenAI-compatible SDK
Ollama SDK

Instead:

Application
    ↓
AI Provider Interface
    ↓
Provider Implementation

The same principle applies to:

Embeddings
Search
Storage
OCR
LLM

where provider abstraction provides meaningful value.

Definition of Done

A phase is not complete merely because the endpoint works.

Every phase should satisfy:

 Architecture consistent
 Domain boundaries clear
 Database migration complete
 Authorization enforced
 Validation implemented
 Error handling implemented
 Relevant tests added
 Full regression tests pass
 Configuration documented
 External dependencies verified
 Failure handling implemented where required
 Documentation updated
 Devlog updated
 Git changes committed
 Branch integration verified
Development Philosophy

DecisionOS should be built incrementally.

Do not optimize for the number of technologies used.

Optimize for the ability to explain:

Why does this component exist?
What problem does it solve?
Where does it belong?
What depends on it?
How does it fail?
How is it tested?
How does it scale?

The ultimate objective is to build a system where:

User
  ↓
Workspace
  ↓
Decision
  ↓
Context
  ↓
Knowledge
  ↓
Research
  ↓
RAG
  ↓
AI Analysis
  ↓
Recommendation
  ↓
Human Decision
  ↓
Outcome
  ↓
Learning

is implemented as a coherent, observable, secure, and model-agnostic platform.

Current Progress
Phase 1  — Foundation
████████████████████ 100% ✅

Phase 2  — Identity
████████████████████ 100% ✅

Phase 3  — Workspace + Decision
████████████████████ 100% ✅

Phase 4  — Knowledge & Ingestion
░░░░░░░░░░░░░░░░░░░░   0%

Phase 5  — RAG Platform
░░░░░░░░░░░░░░░░░░░░   0%

Phase 6  — Context & Prompt Engineering
░░░░░░░░░░░░░░░░░░░░   0%

Phase 7  — Decision Context & Alternatives
░░░░░░░░░░░░░░░░░░░░   0%

Phase 8  — AI Runtime
░░░░░░░░░░░░░░░░░░░░   0%

Phase 9  — Agent Runtime
░░░░░░░░░░░░░░░░░░░░   0%

Phase 10 — Deep Research
░░░░░░░░░░░░░░░░░░░░   0%

Phase 11 — Decision Intelligence
░░░░░░░░░░░░░░░░░░░░   0%

Phase 12 — Memory + Knowledge Graph
░░░░░░░░░░░░░░░░░░░░   0%

Phase 13 — GraphRAG
░░░░░░░░░░░░░░░░░░░░   0%

Phase 14 — Productivity Integrations
░░░░░░░░░░░░░░░░░░░░   0%

Phase 15 — Multimodal
░░░░░░░░░░░░░░░░░░░░   0%

Phase 16 — AI Evaluation & Observability
░░░░░░░░░░░░░░░░░░░░   0%

Phase 17 — Production Engineering
░░░░░░░░░░░░░░░░░░░░   0%

Current milestone: Phase 4 — Knowledge & Ingestion Platform