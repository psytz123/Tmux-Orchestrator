#!/bin/bash
#
# Plan Mode Activation Script
# Activates Claude's plan mode for complex tasks requiring thoughtful decomposition
# Incorporates Agent-MCP patterns for task breakdown
#

TARGET=$1
TASK=$2

if [ -z "$TARGET" ] || [ -z "$TASK" ]; then
    echo "Usage: $0 <session:window> '<task description>'"
    echo "Example: $0 frontend:0 'Implement authentication system with JWT tokens'"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 ACTIVATING PLAN MODE for $TARGET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Send Shift+Tab+Tab to activate plan mode
echo "Sending plan mode activation sequence..."
tmux send-keys -t $TARGET S-Tab S-Tab

# Wait for activation
sleep 2

# Verify plan mode is active
PLAN_MODE_ACTIVE=$(tmux capture-pane -t $TARGET -p -S -5 | grep "plan mode on")

# Retry if not activated
if [ -z "$PLAN_MODE_ACTIVE" ]; then
    echo "Plan mode not activated, retrying..."
    tmux send-keys -t $TARGET S-Tab
    sleep 1
    
    # Check again
    PLAN_MODE_ACTIVE=$(tmux capture-pane -t $TARGET -p -S -5 | grep "plan mode on")
    
    if [ -z "$PLAN_MODE_ACTIVE" ]; then
        echo "⚠️ WARNING: Could not verify plan mode activation"
        echo "You may need to manually activate with Shift+Tab+Tab"
    fi
fi

# Prepare comprehensive planning prompt
PLANNING_PROMPT="Create a detailed implementation plan for: $TASK

Your plan should include:

1. TASK DECOMPOSITION
   - Break this into atomic, linear subtasks
   - Each subtask should be completable in <15 minutes
   - Identify dependencies between subtasks

2. MCP TOOL SELECTION
   - For each subtask, specify the PRIMARY MCP tool to use
   - Examples: mcp__filesystem, mcp__git, mcp__fastapi, mcp__memory
   - NEVER use standard Read/Write/Bash tools

3. SUCCESS CRITERIA
   - Define measurable success for each subtask
   - Include performance metrics where applicable
   - Specify test coverage requirements

4. RISK ASSESSMENT
   - Identify potential blockers
   - Note areas requiring web research
   - Flag any missing dependencies

5. PARALLELIZATION OPPORTUNITIES
   - Which subtasks can run simultaneously?
   - Which require file locks?
   - Optimal agent allocation strategy

6. KNOWLEDGE GRAPH ENTRIES
   - What patterns should be stored in mcp__memory?
   - What existing knowledge is relevant?
   - Key learnings to document

FORMAT YOUR PLAN AS:
━━━━━━━━━━━━━━━━━━━━━
SUBTASK 1: [Clear objective]
MCP_TOOL: [Primary tool]
SUCCESS: [Measurable criteria]
TIME: [Minutes]
DEPENDS_ON: [Previous subtasks]
━━━━━━━━━━━━━━━━━━━━━

Remember: This plan will be executed by ephemeral agents with LIMITED context."

# Send planning task
echo "Sending planning prompt..."
./send-claude-message.sh $TARGET "$PLANNING_PROMPT"

echo ""
echo "✅ Plan mode activated and task sent"
echo "Wait for agent to complete planning before proceeding"
echo ""
echo "Next steps:"
echo "1. Review the generated plan"
echo "2. Use task_assigner.py to distribute subtasks"
echo "3. Monitor progress with cross_window_monitor.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"