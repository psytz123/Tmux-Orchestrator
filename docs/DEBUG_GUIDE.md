# Debugging Guide for Tmux Orchestrator Scripts

## Common Issues and Solutions

### 1. Line Ending Issues (CRLF vs LF)

**Problem:** Scripts fail with errors like `$'\r': command not found`

**Cause:** Windows line endings (CRLF) in scripts

**Solution:**
```bash
# Fix all shell scripts
for script in scripts/*.sh send-claude-message.sh schedule_with_note.sh; do
    sed -i 's/\r$//' "$script"
    chmod +x "$script"
done

# Fix Python scripts (usually not needed)
for script in scripts/*.py monitoring/*.py; do
    sed -i 's/\r$//' "$script"
    chmod +x "$script"
done
```

### 2. Script Execution Issues

**Problem:** `cannot execute: required file not found`

**Solution:**
```bash
# Make all scripts executable
chmod +x scripts/*.py scripts/*.sh
chmod +x monitoring/*.py
chmod +x send-claude-message.sh
chmod +x schedule_with_note.sh
```

### 3. Tmux Window Indexing

**Problem:** Scripts expect window 0 but tmux creates window 1

**Cause:** Tmux may start window indexing at 1 instead of 0

**Solution:**
```bash
# Check window indices
tmux list-windows -t session-name

# Use correct index in commands
./scripts/task_assigner.py --assign session:1 '{"objective":"task"}'
```

### 4. Path Issues

**Problem:** Scripts can't find other scripts

**Solution:** Always run scripts from the orchestrator base directory:
```bash
cd /mnt/c/Users/psytz/TMUX\ Final/Tmux-Orchestrator
./scripts/activate_plan_mode.sh session:window "task"
```

## Testing Scripts

### Test activate_plan_mode.sh

```bash
# Create test session
tmux new-session -d -s test-plan

# Get window index
tmux list-windows -t test-plan

# Test plan mode (use correct window index)
./scripts/activate_plan_mode.sh test-plan:1 "Test planning task"

# Check output
tmux capture-pane -t test-plan:1 -p | tail -20

# Clean up
tmux kill-session -t test-plan
```

### Test task_assigner.py

```bash
# Show available tasks
python3 scripts/task_assigner.py --queue

# Create test session
tmux new-session -d -s test-task

# Assign task (check window index first!)
python3 scripts/task_assigner.py --assign test-task:1 \
  '{"objective":"Test task","mcp_tool":"mcp__filesystem","success_criteria":"Complete","time_limit":5}'

# Check status
python3 scripts/task_assigner.py --check test-task:1

# Monitor all tasks
python3 scripts/task_assigner.py --monitor

# Clean up
tmux kill-session -t test-task
```

### Test MCP Compliance Monitor

```bash
# Check all sessions
python3 scripts/verify_mcp_usage.py --all

# Check specific window
python3 scripts/verify_mcp_usage.py --session test-session --window 1

# Continuous monitoring
python3 scripts/verify_mcp_usage.py --watch --interval 60
```

### Test Cross-Window Monitor

```bash
# One-time scan
python3 monitoring/cross_window_monitor.py --all

# Generate report
python3 monitoring/cross_window_monitor.py --report

# Continuous monitoring
python3 monitoring/cross_window_monitor.py --monitor --interval 30
```

## Verifying Installation

Run the comprehensive validation:
```bash
python3 tests/validate_installation.py
```

Expected output:
- All directory checks: ✅
- All file checks: ✅
- All import checks: ✅
- 100% success rate

## Common Script Parameters

### activate_plan_mode.sh
```bash
./scripts/activate_plan_mode.sh <session:window> "<task description>"
```

### task_assigner.py
```bash
# Assign task
python3 scripts/task_assigner.py --assign <session:window> '<json_task>'

# Check status
python3 scripts/task_assigner.py --check <session:window>

# Complete task
python3 scripts/task_assigner.py --complete <session:window>

# Monitor all
python3 scripts/task_assigner.py --monitor
```

### verify_mcp_usage.py
```bash
# Check all agents
python3 scripts/verify_mcp_usage.py --all

# Watch continuously
python3 scripts/verify_mcp_usage.py --watch --interval 120
```

### cross_window_monitor.py
```bash
# Scan specific window
python3 monitoring/cross_window_monitor.py --scan <session> <window>

# Monitor continuously
python3 monitoring/cross_window_monitor.py --monitor --interval 30
```

## Troubleshooting Checklist

1. ✅ Check tmux is installed: `which tmux`
2. ✅ Fix line endings: `sed -i 's/\r$//' script.sh`
3. ✅ Make executable: `chmod +x script.sh`
4. ✅ Check window exists: `tmux list-windows -t session`
5. ✅ Run from base directory: `cd /mnt/c/Users/psytz/TMUX\ Final/Tmux-Orchestrator`
6. ✅ Verify Python imports: `python3 -c "from scripts.verify_mcp_usage import MCPComplianceMonitor"`

## Quick Debug Commands

```bash
# See what's in a window
tmux capture-pane -t session:window -p | tail -50

# List all sessions and windows
for s in $(tmux list-sessions -F '#{session_name}'); do
    echo "Session: $s"
    tmux list-windows -t $s
done

# Check if script has Windows line endings
file script.sh | grep CRLF

# Fix all line endings at once
find . -name "*.sh" -o -name "*.py" | xargs sed -i 's/\r$//'

# Make all scripts executable
find . -name "*.sh" -o -name "*.py" | xargs chmod +x
```

## Expected Script Outputs

### Successful task assignment:
```
✅ Assigned TASK-20241207-0001 to session:window
Assigned: TASK-20241207-0001
```

### Successful MCP compliance check:
```
MCP COMPLIANCE REPORT
=====================
✅ Agent: session:window
   Compliance Score: 100%
   MCP Tools Used:
   + mcp__filesystem (5 calls)
```

### Successful cross-window scan:
```
CROSS-WINDOW INTELLIGENCE REPORT
================================
✅ No issues detected across all windows
```

## Contact Points

If scripts still fail after following this guide:

1. Run validation: `python3 tests/validate_installation.py`
2. Check test report: `cat tests/TEST_REPORT.md`
3. Review error logs in `monitoring/alerts.log`
4. Ensure all dependencies are installed