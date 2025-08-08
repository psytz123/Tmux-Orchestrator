#!/bin/bash

echo "🔄 Restarting eFab AI Enhanced Application..."
echo "============================================"

# Kill any existing Streamlit processes
echo "Stopping existing Streamlit instances..."
pkill -f streamlit 2>/dev/null || true
pkill -f "python.*streamlit" 2>/dev/null || true

# Kill any existing uvicorn/FastAPI processes
echo "Stopping existing API instances..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "python.*uvicorn" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Start the Streamlit UI
echo ""
echo "🚀 Starting Streamlit UI..."
echo "============================================"
cd "/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/eFab-AI-Enhanced"

# Start Streamlit in background
nohup streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
STREAMLIT_PID=$!

echo "✅ Streamlit started (PID: $STREAMLIT_PID)"
echo ""
echo "📊 Access the application at:"
echo "   http://localhost:8501"
echo ""
echo "📁 Logs available at: streamlit.log"
echo ""
echo "To view logs: tail -f streamlit.log"
echo "To stop: pkill -f streamlit"
echo ""
echo "============================================"
echo "✅ Application restarted successfully!"
echo "============================================"