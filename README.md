# VoiceFlow AI

VoiceFlow AI is a production-ready, multi-tenant AI voice sales agent platform. It enables organizations to deploy multilingual AI representatives to handle incoming and outgoing voice interactions for lead generation, cold calling, appointment booking, and customer support.

---

## Features

| Feature Area | Description |
|---|---|
| **Multilingual Voice Processing** | Automatic detection and switching between English, Hindi, and Bengali. |
| **Agentic Conversation Flow** | Stateful, multi-turn interaction models powered by LangGraph, with robust objection-handling capabilities. |
| **Retrieval-Augmented Generation (RAG)** | Knowledge-base ingestion supporting PDF, DOCX, and CSV formats, scoped specifically to tenant documents. |
| **CRM Integration & Analytics** | Lead scoring, pipeline status tracking, and real-time dashboard visualization. |
| **Calendar Scheduling** | Automated appointment booking integrated with Google Calendar and Zoom. |
| **Outbound Communication** | Automatic notification dispatch via WhatsApp Business API and SMTP email. |
| **Multi-Tenant Architecture** | Tenant-specific branding, system prompts, schemas, and custom AI personality configurations. |
| **Security & Isolation** | JSON Web Token (JWT) authentication, Role-Based Access Control (RBAC), database tenant isolation, and rate-limiting. |
| **Self-Hosted Deployment** | Containerized architecture designed to run on local or private cloud infrastructure. |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                       │
├─────────────┬───────────────────────────────┬───────────────┤
│  Next.js 15 │      FastAPI Backend          │  WebSocket    │
│  Dashboard  │  ┌─────────┐  ┌───────────┐  │  Voice Stream │
│             │  │ Auth/CRM │  │ RAG/Vector│  │               │
│             │  └────┬─────┘  └─────┬─────┘  │               │
│             │       │              │        │               │
│             │  ┌────┴──────────────┴────┐   │               │
│             │  │   LangGraph Agent      │   │               │
│             │  │  ┌─────┐  ┌────────┐   │   │               │
│             │  │  │ STT │→│  LLM   │   │   │               │
│             │  │  │Whisp│  │ Ollama │   │   │               │
│             │  │  └─────┘  └────────┘   │   │               │
│             │  │  ┌─────┐               │   │               │
│             │  │  │ TTS │ Piper         │   │               │
│             │  │  └─────┘               │   │               │
│             │  └────────────────────────┘   │               │
├─────────────┴───────────────────────────────┴───────────────┤
│  PostgreSQL  │  Redis  │  Qdrant  │  Ollama  │  Celery      │
└──────────────┴─────────┴──────────┴──────────┴──────────────┘
```

---

## Tech Stack

| Component | Technologies |
|---|---|
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS, Framer Motion |
| **Backend** | FastAPI, Python, SQLAlchemy, Alembic |
| **AI/ML** | LangGraph, LiteLLM, Ollama, Faster Whisper, Piper TTS |
| **Databases** | PostgreSQL, Redis, Qdrant |
| **Message Queue** | Celery |
| **Reverse Proxy** | Nginx |

---

## Project Directory Layout

```
voiceflow-ai/
├── backend/               # FastAPI backend codebase
│   └── src/
│       ├── ai/            # Voice processing, LLM wrappers, LangGraph agent
│       ├── auth/          # JWT authentication and Role-Based Access Control
│       ├── crm/           # CRM routers and data persistence
│       ├── rag/           # Document parser and retriever modules
│       ├── integrations/  # External APIs (Email, WhatsApp, Calendar)
│       ├── models/        # SQLAlchemy schemas
│       └── workers/       # Celery background tasks
├── frontend/              # Next.js frontend application
│   └── src/
│       ├── app/           # App router views (Dashboard, voice, leads, etc.)
│       ├── components/    # Common UI components
│       ├── hooks/         # Custom React hooks
│       └── lib/           # Auth contexts, API clients
├── docker/                # Production service configurations (Nginx, etc.)
├── docs/                  # API and deployment specifications
└── scripts/               # Bootstrapping and orchestration helpers
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Minimum 8 GB RAM (16 GB recommended for running local LLM inference)
- Git

### 1. Configuration

Clone the repository and prepare the configuration files:

```bash
git clone <repository-url>
cd voiceflow-ai
cp .env.example .env
```

Ensure the configuration variables in `.env` are updated for your environment.

### 2. Service Initialization

Launch the required background services (databases, queues, caches):

```bash
docker compose up -d
```

### 3. Model Provisioning

Download the required local LLM and embedding models (first-time setup):

```bash
# Retrieve the LLM model
docker exec -it voiceflow-ai-ollama-1 ollama pull llama3.1:8b

# Retrieve the embedding model
docker exec -it voiceflow-ai-ollama-1 ollama pull nomic-embed-text
```

### 4. Database Migrations

Apply database migrations to set up the schemas:

```bash
docker exec -it voiceflow-ai-backend-1 alembic upgrade head
```

---

## API Reference

### Authentication Endpoints

| Method | URI | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new tenant and administrative user. |
| `POST` | `/api/v1/auth/login` | Authenticate user and issue tokens. |
| `POST` | `/api/v1/auth/refresh` | Refresh an access token. |
| `GET` | `/api/v1/auth/me` | Retrieve the authenticated user's profile. |

### CRM Endpoints

| Method | URI | Description |
|---|---|---|
| `GET` | `/api/v1/leads` | List leads with filtering and pagination. |
| `POST` | `/api/v1/leads` | Create a new lead record. |
| `GET` | `/api/v1/leads/{id}` | Retrieve a specific lead record. |
| `PUT` | `/api/v1/leads/{id}` | Update an existing lead record. |
| `DELETE` | `/api/v1/leads/{id}` | Remove a lead record. |
| `GET` | `/api/v1/conversations` | List conversation records. |
| `GET` | `/api/v1/analytics/dashboard` | Retrieve analytics for the dashboard view. |

### Knowledge Base Endpoints

| Method | URI | Description |
|---|---|---|
| `POST` | `/api/v1/knowledge/upload` | Upload a document for RAG ingestion. |
| `GET` | `/api/v1/knowledge/documents` | List uploaded knowledge documents. |
| `POST` | `/api/v1/knowledge/query` | Test query against the RAG system. |

### Voice Interface

| Protocol | URI | Description |
|---|---|---|
| `WebSocket` | `/ws/voice` | Establish real-time bidirectional audio streaming. |

---

## Supported Languages

| Language | Speech-to-Text (STT) | Text-to-Speech (TTS) | AI Agent Support |
|---|---|---|---|
| English | Yes (Faster Whisper) | Yes (Piper) | Yes |
| Hindi | Yes (Faster Whisper) | Yes (Piper) | Yes |
| Bengali | Yes (Faster Whisper) | Experimental | Yes |

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
