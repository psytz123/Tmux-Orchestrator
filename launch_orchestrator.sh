#!/bin/bash
#
# Launch Script for Tmux Orchestrator
# Starts all monitoring systems and creates orchestrator session
#

BASE_DIR="/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator"
cd "$BASE_DIR" || exit 1

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 LAUNCHING TMUX ORCHESTRATOR SYSTEM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Create orchestrator session if it doesn't exist
echo "1️⃣ Setting up orchestrator session..."
if ! tmux has-session -t tmux-orchestrator 2>/dev/null; then
    tmux new-session -d -s tmux-orchestrator -n "orchestrator" -c "$BASE_DIR"
    echo "✅ Created tmux-orchestrator session"
else
    echo "✅ tmux-orchestrator session already exists"
fi

# 2. Start monitoring windows
echo ""
echo "2️⃣ Starting monitoring systems..."

# Auto-commit monitor
if ! tmux has-session -t tmux-orchestrator 2>/dev/null || ! tmux list-windows -t tmux-orchestrator | grep -q "auto-commit"; then
    tmux new-window -t tmux-orchestrator -n "auto-commit" -c "$BASE_DIR"
    tmux send-keys -t tmux-orchestrator:auto-commit "cd '$BASE_DIR' && ./scripts/auto_git_commit.sh 1800" Enter
    echo "✅ Started auto-commit system (30-minute interval)"
else
    echo "✅ Auto-commit already running"
fi

# Cross-window monitor
if ! tmux list-windows -t tmux-orchestrator | grep -q "cross-monitor"; then
    tmux new-window -t tmux-orchestrator -n "cross-monitor" -c "$BASE_DIR"
    tmux send-keys -t tmux-orchestrator:cross-monitor "cd '$BASE_DIR' && python3 monitoring/cross_window_monitor.py --monitor --interval 30" Enter
    echo "✅ Started cross-window monitoring (30-second interval)"
else
    echo "✅ Cross-window monitor already running"
fi

# MCP compliance monitor
if ! tmux list-windows -t tmux-orchestrator | grep -q "mcp-monitor"; then
    tmux new-window -t tmux-orchestrator -n "mcp-monitor" -c "$BASE_DIR"
    tmux send-keys -t tmux-orchestrator:mcp-monitor "cd '$BASE_DIR' && python3 scripts/verify_mcp_usage.py --watch --interval 120" Enter
    echo "✅ Started MCP compliance monitoring (2-minute interval)"
else
    echo "✅ MCP monitor already running"
fi

# 3. Create agent briefing in orchestrator window
echo ""
echo "3️⃣ Preparing orchestrator briefing..."

BRIEFING="Welcome to the Tmux Orchestrator!

You are the master orchestrator managing multiple Claude agents across tmux sessions.

Key Responsibilities:
1. Deploy and coordinate agent teams
2. Monitor system health via monitoring windows
3. Enforce MCP-first development
4. Ensure git commits every 30 minutes
5. Track task completion and quality

Available Monitoring:
- Window 'auto-commit': Auto-commits all work every 30 minutes
- Window 'cross-monitor': Detects errors across all windows
- Window 'mcp-monitor': Tracks MCP tool compliance

Key Commands:
- Assign tasks: python3 scripts/task_assigner.py --assign <session:window> '<task_json>'
- Check compliance: python3 scripts/verify_mcp_usage.py --all
- View errors: python3 monitoring/cross_window_monitor.py --report
- Activate plan mode: ./scripts/activate_plan_mode.sh <session:window> '<task>'

MCP Tools Available:
- mcp__filesystem (5-10x faster than Read/Write)
- mcp__git (for version control)
- mcp__memory (knowledge persistence)
- mcp__[framework] (framework patterns)

Remember:
- Credits are limited - every message costs money
- Enforce single-task protocol
- Replace non-compliant agents after 3 strikes
- Proactive monitoring saves time and credits

Current Status:
✅ Auto-commit system: RUNNING
✅ Cross-window monitor: RUNNING  
✅ MCP compliance: RUNNING
✅ All systems operational

Type 'tmux list-windows' to see all monitoring windows.
Type 'tmux capture-pane -t tmux-orchestrator:<window> -p | tail -50' to check any monitor."

# Save briefing to file
echo "$BRIEFING" > "$BASE_DIR/registry/orchestrator_briefing.txt"
echo "✅ Orchestrator briefing prepared"

# 4. Display status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ORCHESTRATOR SYSTEM LAUNCHED SUCCESSFULLY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Session: tmux-orchestrator"
echo "Windows:"
tmux list-windows -t tmux-orchestrator 2>/dev/null || echo "  (listing unavailable)"
echo ""
echo "To enter orchestrator:"
echo "  tmux attach -t tmux-orchestrator"
echo ""
echo "To start Claude in orchestrator:"
echo "  1. Attach to session: tmux attach -t tmux-orchestrator"
echo "  2. Start Claude: claude --dangerously-skip-permissions"
echo "  3. Copy briefing from: registry/orchestrator_briefing.txt"
echo ""
echo "Quick status checks:"
echo "  Check auto-commits: tmux capture-pane -t tmux-orchestrator:auto-commit -p | tail -20"
echo "  Check errors: tmux capture-pane -t tmux-orchestrator:cross-monitor -p | tail -20"
echo "  Check MCP: tmux capture-pane -t tmux-orchestrator:mcp-monitor -p | tail -20"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"