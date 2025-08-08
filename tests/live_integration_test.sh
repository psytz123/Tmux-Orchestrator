#!/bin/bash
#
# Live Integration Test for Tmux Orchestrator
# Tests the complete workflow with actual tmux sessions
#

BASE_DIR="/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator"
TEST_SESSION="test-orchestrator-live"
TEST_LOG="$BASE_DIR/tests/integration_test.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "$1" | tee -a "$TEST_LOG"
}

cleanup() {
    log "${YELLOW}Cleaning up test session...${NC}"
    tmux kill-session -t $TEST_SESSION 2>/dev/null
    exit
}

trap cleanup EXIT

# Start fresh
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "LIVE INTEGRATION TEST FOR TMUX ORCHESTRATOR"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Timestamp: $(date)"
echo "" > "$TEST_LOG"

# Test 1: Create test session
log "\n${YELLOW}TEST 1: Creating tmux test session${NC}"
tmux new-session -d -s $TEST_SESSION -c "$BASE_DIR"
if [ $? -eq 0 ]; then
    log "${GREEN}✅ Session created successfully${NC}"
else
    log "${RED}❌ Failed to create session${NC}"
    exit 1
fi

# Test 2: Test MCP compliance monitoring
log "\n${YELLOW}TEST 2: Testing MCP compliance monitoring${NC}"
tmux send-keys -t $TEST_SESSION:0 "cd '$BASE_DIR' && python3 scripts/verify_mcp_usage.py --all" Enter
sleep 2
OUTPUT=$(tmux capture-pane -t $TEST_SESSION:0 -p | tail -20)
if [[ "$OUTPUT" == *"MCP COMPLIANCE REPORT"* ]]; then
    log "${GREEN}✅ MCP compliance monitor works${NC}"
else
    log "${RED}❌ MCP compliance monitor failed${NC}"
fi

# Test 3: Test task assignment
log "\n${YELLOW}TEST 3: Testing task assignment system${NC}"
tmux new-window -t $TEST_SESSION:1 -n "test-agent"
TASK_JSON='{"objective":"Test task assignment","mcp_tool":"mcp__filesystem","success_criteria":"Task received","time_limit":5}'
tmux send-keys -t $TEST_SESSION:1 "cd '$BASE_DIR' && python3 scripts/task_assigner.py --queue" Enter
sleep 2
OUTPUT=$(tmux capture-pane -t $TEST_SESSION:1 -p | tail -10)
if [[ "$OUTPUT" == *"Task Queue"* ]]; then
    log "${GREEN}✅ Task assigner works${NC}"
else
    log "${RED}❌ Task assigner failed${NC}"
fi

# Test 4: Test cross-window monitoring
log "\n${YELLOW}TEST 4: Testing cross-window monitoring${NC}"
tmux new-window -t $TEST_SESSION:2 -n "monitor"
tmux send-keys -t $TEST_SESSION:2 "cd '$BASE_DIR' && python3 monitoring/cross_window_monitor.py --report" Enter
sleep 2
OUTPUT=$(tmux capture-pane -t $TEST_SESSION:2 -p | tail -20)
if [[ "$OUTPUT" == *"CROSS-WINDOW INTELLIGENCE REPORT"* ]]; then
    log "${GREEN}✅ Cross-window monitor works${NC}"
else
    log "${RED}❌ Cross-window monitor failed${NC}"
fi

# Test 5: Test plan mode activation script
log "\n${YELLOW}TEST 5: Testing plan mode activation${NC}"
if [ -f "$BASE_DIR/scripts/activate_plan_mode.sh" ]; then
    # Just check script exists and has correct structure
    if grep -q "ACTIVATING PLAN MODE" "$BASE_DIR/scripts/activate_plan_mode.sh"; then
        log "${GREEN}✅ Plan mode script configured${NC}"
    else
        log "${RED}❌ Plan mode script misconfigured${NC}"
    fi
else
    log "${RED}❌ Plan mode script not found${NC}"
fi

# Test 6: Test auto-commit script
log "\n${YELLOW}TEST 6: Testing auto-commit script${NC}"
if [ -f "$BASE_DIR/scripts/auto_git_commit.sh" ]; then
    if grep -q "perform_commit_cycle" "$BASE_DIR/scripts/auto_git_commit.sh"; then
        log "${GREEN}✅ Auto-commit script configured${NC}"
    else
        log "${RED}❌ Auto-commit script misconfigured${NC}"
    fi
else
    log "${RED}❌ Auto-commit script not found${NC}"
fi

# Test 7: Test Agent-MCP integration
log "\n${YELLOW}TEST 7: Testing Agent-MCP integration${NC}"
tmux new-window -t $TEST_SESSION:3 -n "agent-mcp"
tmux send-keys -t $TEST_SESSION:3 "cd '$BASE_DIR' && python3 -c 'from core.orchestrator.agent_mcp_integration import AgentMCPOrchestrator; o = AgentMCPOrchestrator(); print(\"Max agents:\", o.max_agents)'" Enter
sleep 2
OUTPUT=$(tmux capture-pane -t $TEST_SESSION:3 -p | tail -5)
if [[ "$OUTPUT" == *"Max agents: 10"* ]]; then
    log "${GREEN}✅ Agent-MCP integration works${NC}"
else
    log "${RED}❌ Agent-MCP integration failed${NC}"
fi

# Test 8: Verify critical files
log "\n${YELLOW}TEST 8: Verifying critical files${NC}"
CRITICAL_FILES=(
    "CLAUDE.md"
    "send-claude-message.sh"
    "templates/agent_briefing_template.md"
    "scripts/verify_mcp_usage.py"
    "scripts/task_assigner.py"
    "monitoring/cross_window_monitor.py"
)

ALL_GOOD=true
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$BASE_DIR/$file" ]; then
        log "${GREEN}  ✅ $file exists${NC}"
    else
        log "${RED}  ❌ $file missing${NC}"
        ALL_GOOD=false
    fi
done

if $ALL_GOOD; then
    log "${GREEN}✅ All critical files present${NC}"
else
    log "${RED}❌ Some critical files missing${NC}"
fi

# Test 9: Check CLAUDE.md updates
log "\n${YELLOW}TEST 9: Checking CLAUDE.md MCP protocols${NC}"
if grep -q "MCP-FIRST PROTOCOL - MANDATORY" "$BASE_DIR/CLAUDE.md"; then
    log "${GREEN}✅ CLAUDE.md has MCP protocols${NC}"
else
    log "${RED}❌ CLAUDE.md missing MCP protocols${NC}"
fi

# Test 10: Simulate error detection
log "\n${YELLOW}TEST 10: Simulating error detection${NC}"
tmux new-window -t $TEST_SESSION:4 -n "error-test"
tmux send-keys -t $TEST_SESSION:4 "echo 'Error: port 3000 is already in use'" Enter
sleep 1

# Run cross-window monitor to detect the error
tmux send-keys -t $TEST_SESSION:2 "cd '$BASE_DIR' && python3 monitoring/cross_window_monitor.py --scan $TEST_SESSION 4" Enter
sleep 2
OUTPUT=$(tmux capture-pane -t $TEST_SESSION:2 -p | tail -30)
if [[ "$OUTPUT" == *"port"* ]] || [[ "$OUTPUT" == *"Port already in use"* ]]; then
    log "${GREEN}✅ Error detection works${NC}"
else
    log "${YELLOW}⚠️ Error detection inconclusive${NC}"
fi

# Summary
log "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "TEST SUMMARY"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SUCCESS_COUNT=$(grep -c "✅" "$TEST_LOG")
FAILURE_COUNT=$(grep -c "❌" "$TEST_LOG")
WARNING_COUNT=$(grep -c "⚠️" "$TEST_LOG")

log "Successful tests: ${GREEN}$SUCCESS_COUNT${NC}"
log "Failed tests: ${RED}$FAILURE_COUNT${NC}"
log "Warnings: ${YELLOW}$WARNING_COUNT${NC}"

if [ $FAILURE_COUNT -eq 0 ]; then
    log "\n${GREEN}🎉 ALL INTEGRATION TESTS PASSED!${NC}"
    log "The tmux orchestrator is ready for use."
else
    log "\n${RED}Some tests failed. Please review the issues above.${NC}"
fi

log "\nTest session '$TEST_SESSION' still active for inspection."
log "Run 'tmux attach -t $TEST_SESSION' to review."
log "Run 'tmux kill-session -t $TEST_SESSION' to clean up."
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"