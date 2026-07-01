#!/bin/bash
# ============================================================
# VoiceFlow AI — One-Command Setup Script
# ============================================================
set -e

echo "🎙️  VoiceFlow AI — Setup Script"
echo "================================"

# 1. Create .env from template
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "   ✅ .env created. Please update secrets before production use."
else
    echo "   ℹ️  .env already exists, skipping."
fi

# 2. Create required directories
echo "📁 Creating directories..."
mkdir -p uploads recordings

# 3. Start Docker services
echo "🐳 Starting Docker services..."
docker compose up -d

# 4. Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 15

# 5. Pull Ollama models
echo "🤖 Pulling AI models (this may take a while on first run)..."
docker exec voiceflow-ai-ollama-1 ollama pull llama3.1:8b 2>/dev/null || \
    docker exec -it $(docker compose ps -q ollama) ollama pull llama3.1:8b || \
    echo "⚠️  Could not pull LLM model. Please run: docker exec <ollama-container> ollama pull llama3.1:8b"

docker exec voiceflow-ai-ollama-1 ollama pull nomic-embed-text 2>/dev/null || \
    docker exec -it $(docker compose ps -q ollama) ollama pull nomic-embed-text || \
    echo "⚠️  Could not pull embedding model. Please run: docker exec <ollama-container> ollama pull nomic-embed-text"

# 6. Run database migrations
echo "🗄️  Running database migrations..."
docker exec voiceflow-ai-backend-1 alembic upgrade head 2>/dev/null || \
    docker exec $(docker compose ps -q backend) alembic upgrade head || \
    echo "⚠️  Migrations may need to be run manually."

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access the application:"
echo "   Frontend:  http://localhost"
echo "   API Docs:  http://localhost/docs"
echo "   Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "🔑 Default credentials: Register a new account at http://localhost"
