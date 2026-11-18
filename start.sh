#!/bin/bash
# Start Inventory Reconciliation SaaS (Reconly)
set -e

export PATH="$HOME/.pyenv/bin:$HOME/.pyenv/shims:$HOME/local/nodejs/bin:$PATH"
cd "$(dirname "$0")"

echo "🚀 Starting Reconly — Inventory Reconciliation SaaS..."

# Start Docker containers
echo "📦 Starting Docker services (PostgreSQL + Redis)..."
docker compose up -d db redis 2>/dev/null || docker compose up -d
sleep 5

# Start backend
echo "⚙️  Starting backend on port 8001..."
source .venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🎨 Starting frontend on port 3000..."
cd frontend
npx vite --port 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================="
echo "  ✅ Reconly is running!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8001"
echo "  API Docs: http://localhost:8001/docs"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop"
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'; exit" INT
wait
