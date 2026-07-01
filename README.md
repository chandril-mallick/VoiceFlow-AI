# 🎙️ VoiceFlow AI

### Your 24/7 AI Sales Representative

A production-ready, multi-tenant AI Voice Sales Agent SaaS platform that enables businesses to deploy multilingual AI sales representatives capable of handling voice conversations for lead generation, cold calling, appointment booking, customer support, and product inquiries.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Multilingual Voice** | Bengali, Hindi, English with automatic detection & switching |
| 🧠 **AI Sales Agent** | LangGraph-powered conversation flow with natural objection handling |
| 📚 **RAG Knowledge Base** | Upload PDFs, DOCX, CSVs — AI answers from YOUR documents only |
| 📊 **CRM & Analytics** | Lead scoring, pipeline management, real-time dashboards |
| 📅 **Appointment Booking** | Google Calendar + Zoom integration |
| 💬 **WhatsApp & Email** | Automated follow-up messaging |
| 🏢 **Multi-Tenant SaaS** | Each business gets own branding, prompts, CRM, and AI personality |
| 🔒 **Enterprise Security** | JWT + RBAC, audit logs, tenant isolation, rate limiting |
| 🐳 **Fully Local** | Runs entirely on Docker — zero cloud dependency |

---

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM (16GB recommended for LLM)
- Git

### 1. Clone & Configure
```bash
git clone <repository-url>
cd voiceflow-ai

# Copy environment template
cp .env.example .env
```

### 2. Start All Services
```bash
docker compose up -d
```

### 3. Pull AI Models (first time only)
```bash
# Pull the LLM model
docker exec -it voiceflow-ai-ollama-1 ollama pull llama3.1:8b

# Pull the embedding model
docker exec -it voiceflow-ai-ollama-1 ollama pull nomic-embed-text
```

### 4. Run Database Migrations
```bash
docker exec -it voiceflow-ai-backend-1 alembic upgrade head
```

### 5. Access the Application
| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost |
| API Documentation | http://localhost/docs |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS, ShadCN UI, Framer Motion |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic |
| **AI** | LangGraph, LiteLLM, Ollama (llama3.1:8b), Faster Whisper, Piper TTS |
| **Database** | PostgreSQL 16, Redis 7, Qdrant (vectors) |
| **Queue** | Celery with Redis broker |
| **Infrastructure** | Docker Compose, Nginx |

---

## 📁 Project Structure

```
voiceflow-ai/
├── backend/               # FastAPI + AI + RAG
│   └── src/
│       ├── ai/            # Voice pipeline, LLM, LangGraph agent
│       ├── auth/          # JWT authentication + RBAC
│       ├── crm/           # CRM router + service
│       ├── rag/           # Document ingestion + Qdrant retriever
│       ├── integrations/  # Email, WhatsApp, Calendar, Webhooks
│       ├── models/        # SQLAlchemy models (8 tables)
│       └── workers/       # Celery background tasks
├── frontend/              # Next.js 15 dashboard
│   └── src/
│       ├── app/           # Pages (dashboard, voice, leads, etc.)
│       ├── components/    # Reusable UI components
│       ├── hooks/         # Custom React hooks
│       └── lib/           # API client, auth, WebSocket
├── docker/                # Dockerfiles + Nginx config
├── docs/                  # API & deployment documentation
└── scripts/               # Setup and seed scripts
```

---

## 🔌 API Overview

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register tenant + admin |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Current user profile |

### CRM
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/v1/leads` | List/Create leads |
| GET/PUT/DELETE | `/api/v1/leads/{id}` | Manage lead |
| GET | `/api/v1/conversations` | List conversations |
| GET | `/api/v1/analytics/dashboard` | Dashboard stats |

### Knowledge Base
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/knowledge/upload` | Upload document |
| GET | `/api/v1/knowledge/documents` | List documents |
| POST | `/api/v1/knowledge/query` | Test RAG query |

### Voice
| WebSocket | `/ws/voice` | Real-time voice streaming |

---

## 🌐 Supported Languages

| Language | STT | TTS | Agent |
|----------|-----|-----|-------|
| 🇺🇸 English | ✅ | ✅ | ✅ |
| 🇮🇳 Hindi | ✅ | ✅ | ✅ |
| 🇧🇩 Bengali | ✅ | ⚠️ | ✅ |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
