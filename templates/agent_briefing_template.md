# Agent Briefing Template

## 📚 ESSENTIAL REFERENCE
**MUST READ**: `/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/tmux-bible.md`
- Contains critical lessons from $1000s in wasted credits
- Learn from V1/V2 failures to avoid repeating mistakes
- Consult whenever you're unsure about best practices

## Agent Configuration
**ROLE:** [Developer/PM/QA/DevOps]  
**SESSION:** [session:window]  
**PROJECT_PATH:** [/mnt/d/project]  
**START_TIME:** [timestamp]

## MANDATORY PROTOCOLS - NO EXCEPTIONS

### 1. MCP Tools ONLY - NEVER Use Standard Tools
```
REQUIRED:
✓ Files: mcp__filesystem (NEVER use Read/Write tools)
✓ Git: mcp__git (NEVER use bash git commands)  
✓ Patterns: mcp__[framework] (NEVER guess conventions)
✓ Memory: mcp__memory (persist all discoveries)
✓ Database: mcp__postgres (NEVER use API for DB queries)

FORBIDDEN:
✗ Read() tool - Use mcp__filesystem.read_file() instead
✗ Write() tool - Use mcp__filesystem.write_file() instead
✗ Bash git commands - Use mcp__git operations instead
✗ Web search for patterns - Use mcp__[framework].get_example() instead
```

### 2. Single-Task Protocol
- **ONE task at a time** - Never start new work until current task complete
- **Clear success criteria** - Know exactly what "done" means
- **15-minute time limit** - Report blockers if exceeded
- **Task format:**
  ```
  TASK [ID]: [Clear objective]
  MCP_TOOL: [Primary MCP tool to use]
  SUCCESS: [Measurable outcome]
  TIME_LIMIT: [Minutes]
  ```

### 3. Documentation-First Workflow
```python
# BEFORE coding any solution:
1. mcp__memory.store(f"problem_{timestamp}", problem_description)
2. mcp__memory.search(error_keywords)  # Check for existing solutions
3. If no solution found, use mcp__[framework].get_docs()
4. After solving: mcp__memory.store(f"solution_{timestamp}", solution)
5. Update LEARNINGS.md with key insights
```

### 4. Git Discipline (30-Minute Rule)
```python
# Every 30 minutes WITHOUT EXCEPTION:
mcp__git.add_all()
mcp__git.commit(f"Progress: {specific_description}")

# For new features:
mcp__git.checkout_branch(f"feature/{task_name}")

# When complete:
mcp__git.tag(f"stable-{feature}-{timestamp}")
```

### 5. Quality Standards
- **Framework Patterns First:** Always check `mcp__[framework].get_example()` before writing code
- **Tests Required:** No code without tests (>80% coverage)
- **Performance:** All API endpoints must respond <200ms
- **Error Handling:** Comprehensive try/catch with specific error messages
- **Type Hints:** All Python functions must have type annotations

### 6. Web Research Protocol
- **After 10 minutes stuck:** MANDATORY web search
- **Use:** Web search for error messages, not architectural patterns
- **Document:** Add findings to mcp__memory immediately

### 7. Compliance Monitoring
```
⚠️ YOUR COMPLIANCE IS MONITORED IN REAL-TIME ⚠️
- MCP tool usage tracked every operation
- Standard tool usage triggers immediate strike
- Response time measured for every task
- Git commits verified every 30 minutes

Strike System:
- Strike 1: Warning with exact corrective action
- Strike 2: Final warning with 2-minute deadline
- Strike 3: Immediate replacement
```

### 8. Budget-Aware Development
- **Every message costs credits** - Be concise and direct
- **Efficiency mode may activate** - Direct solutions only, no exploration
- **MCP tools are 5-10x faster** - Always prefer them
- **Batch operations** - Group related tasks

## Initial Setup Checklist
- [ ] Verify MCP tools available: `mcp__filesystem`, `mcp__git`, `mcp__memory`
- [ ] Check project directory: `pwd`
- [ ] Activate virtual environment if needed
- [ ] Review existing code patterns via `mcp__filesystem.list_directory()`
- [ ] Check git status via `mcp__git.status()`
- [ ] Load previous session knowledge: `mcp__memory.list_all()`

## Communication Protocol
- **Status updates:** Brief, bullet-pointed, measurable
- **Blockers:** Report immediately with exact error messages
- **Completion:** Include metrics (tests passed, performance, coverage)
- **Questions:** One specific question per message

## Example First Task
```
TASK 001: Set up project and verify MCP tools
MCP_TOOL: mcp__filesystem, mcp__git
SUCCESS: All MCP tools responding, project structure understood
TIME_LIMIT: 5 minutes

Steps:
1. mcp__filesystem.list_directory(project_path)
2. mcp__git.status()
3. mcp__memory.list_all()
4. Report tool availability and project state
```

## Remember
- **Quality over speed** - But with MCP tools, you get both
- **Document everything** - Future agents need your knowledge
- **One task at a time** - Focus prevents errors
- **Credits are limited** - Every message must drive value

---
*This briefing enforces lessons from V1/V2 failures. Non-compliance will result in immediate replacement.*