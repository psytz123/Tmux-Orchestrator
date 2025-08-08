![Orchestrator Hero](/Orchestrator.png)

**Run AI agents 24/7 while you sleep** - The Tmux Orchestrator enables Claude agents to work autonomously, schedule their own check-ins, and coordinate across multiple projects without human intervention.

## 📚 Essential Reading: tmux-bible.md

**Before starting, READ THIS FIRST:**
`/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/tmux-bible.md`

This critical document contains hard-learned lessons from $1000s in wasted credits, including:
- Why V1 failed (manual orchestration doesn't work)
- Why V2 failed (PMs need proactive monitoring)
- How to prevent work loss (git discipline)
- Credit optimization strategies
- Agent compliance tactics

⚠️ **Warning**: Ignoring tmux-bible.md will result in repeating expensive mistakes!

## 🤖 Key Capabilities & Autonomous Features

- **Self-trigger** - Agents schedule their own check-ins and continue work autonomously
- **Coordinate** - Project managers assign tasks to engineers across multiple codebases  
- **Persist** - Work continues even when you close your laptop
- **Scale** - Run multiple teams working on different projects simultaneously
- **MCP-First** - 5-10x faster development with Model Context Protocol tools
- **Auto-Commit** - Prevents work loss with automatic git commits every 30 minutes
- **Cross-Window Intelligence** - Proactive error detection and resolution across all agents
- **Compliance Monitoring** - Enforces MCP usage with automated strike system

## 🏗️ Architecture

The Tmux Orchestrator uses a three-tier hierarchy to overcome context window limitations:

```
┌─────────────┐
│ Orchestrator│ ← You interact here
└──────┬──────┘
       │ Monitors & coordinates
       ▼
┌─────────────┐     ┌─────────────┐
│  Project    │     │  Project    │
│  Manager 1  │     │  Manager 2  │ ← Assign tasks, enforce specs
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ Engineer 1  │     │ Engineer 2  │ ← Write code, fix bugs
└─────────────┘     └─────────────┘
```

### Why Separate Agents?
- **Limited context windows** - Each agent stays focused on its role
- **Specialized expertise** - PMs manage, engineers code
- **Parallel work** - Multiple engineers can work simultaneously
- **Better memory** - Smaller contexts mean better recall

## 📸 Examples in Action

### Project Manager Coordination
![Initiate Project Manager](Examples/Initiate%20Project%20Manager.png)
*The orchestrator creating and briefing a new project manager agent*

### Status Reports & Monitoring
![Status Reports](Examples/Status%20reports.png)
*Real-time status updates from multiple agents working in parallel*

### Tmux Communication
![Reading TMUX Windows and Sending Messages](Examples/Reading%20TMUX%20Windows%20and%20Sending%20Messages.png)
*How agents communicate across tmux windows and sessions*

### Project Completion
![Project Completed](Examples/Project%20Completed.png)
*Successful project completion with all tasks verified and committed*

## 🚀 Automated Launch

Start the entire orchestrator system with all monitoring:

```bash
# Launch orchestrator with auto-commit, error detection, and MCP monitoring
./launch_orchestrator.sh

# This automatically starts:
# - Auto-commit system (30-minute intervals)
# - Cross-window error monitoring (30-second checks)
# - MCP compliance monitoring (2-minute checks)
# - Orchestrator session ready for Claude
```

## 🎯 Quick Start

### Option 1: Basic Setup (Single Project)

```bash
# 1. Create a project spec
cat > project_spec.md << 'EOF'
PROJECT: My Web App
GOAL: Add user authentication system
CONSTRAINTS:
- Use existing database schema
- Follow current code patterns  
- Commit every 30 minutes
- Write tests for new features

DELIVERABLES:
1. Login/logout endpoints
2. User session management
3. Protected route middleware
EOF

# 2. Start tmux session
tmux new-session -s my-project

# 3. Start project manager in window 0
claude --dangerously-skip-permissions

# 4. Give PM the spec and let it create an engineer
"You are a Project Manager. Read project_spec.md and create an engineer 
in window 1 to implement it. Schedule check-ins every 30 minutes."

# 5. Schedule orchestrator check-in
./schedule_with_note.sh 30 "Check PM progress on auth system"
```

### Option 2: Full Orchestrator Setup

```bash
# Start the orchestrator
tmux new-session -s orchestrator
claude --dangerously-skip-permissions

# Give it your projects
"You are the Orchestrator. Set up project managers for:
1. Frontend (React app) - Add dashboard charts
2. Backend (FastAPI) - Optimize database queries
Schedule yourself to check in every hour."
```

## ✨ Key Features

### 🔄 Self-Scheduling Agents
Agents can schedule their own check-ins using:
```bash
./schedule_with_note.sh 30 "Continue dashboard implementation"
```

### 👥 Multi-Agent Coordination
- Project managers communicate with engineers
- Orchestrator monitors all project managers
- Cross-project knowledge sharing
- Single-task protocol prevents agent confusion

### 💾 Automatic Git Backups
- Commits every 30 minutes of work automatically
- Tags stable versions every 6 commits
- Creates feature branches for experiments
- MCP git integration for faster operations

### 📊 Real-Time Monitoring
- See what every agent is doing
- Proactive error detection across all windows
- MCP compliance tracking with strike system
- Intervene when needed
- Review progress across all projects

### ⚡ MCP-First Development (5-10x Faster)
- `mcp__filesystem` replaces slow Read/Write operations
- `mcp__git` for instant version control
- `mcp__memory` for persistent knowledge sharing
- Framework-specific patterns via `mcp__[framework]`
- Direct database access with `mcp__postgres`

### 🛡️ Advanced Safety Systems
- **Auto-commit monitoring**: Prevents work loss
- **Cross-window intelligence**: Catches errors before they cascade
- **MCP compliance enforcement**: 3-strike system for non-compliant agents
- **Single-task assignment**: Prevents context overload
- **Ephemeral agents**: Limited-lifespan agents for focused tasks

## 📋 Best Practices

### Writing Effective Specifications

```markdown
PROJECT: E-commerce Checkout
GOAL: Implement multi-step checkout process

CONSTRAINTS:
- Use existing cart state management
- Follow current design system
- Maximum 3 API endpoints
- Commit after each step completion

DELIVERABLES:
1. Shipping address form with validation
2. Payment method selection (Stripe integration)
3. Order review and confirmation page
4. Success/failure handling

SUCCESS CRITERIA:
- All forms validate properly
- Payment processes without errors  
- Order data persists to database
- Emails send on completion
```

### Git Safety Rules

1. **Before Starting Any Task**
   ```bash
   git checkout -b feature/[task-name]
   git status  # Ensure clean state
   ```

2. **Every 30 Minutes**
   ```bash
   git add -A
   git commit -m "Progress: [what was accomplished]"
   ```

3. **When Task Completes**
   ```bash
   git tag stable-[feature]-[date]
   git checkout main
   git merge feature/[task-name]
   ```

## 🚨 Common Pitfalls & Solutions

| Pitfall | Consequence | Solution | tmux-bible.md Reference |
|---------|-------------|----------|------------------------|
| Vague instructions | Agent drift, wasted compute | Write clear, specific specs | Section: "Agent Psychology" |
| No git commits | Lost work, frustrated devs | Enforce 30-minute commit rule | Section: "Git Discipline" |
| Too many tasks | Context overload, confusion | One task per agent at a time | Section: "Single Task Protocol" |
| No specifications | Unpredictable results | Always start with written spec | Section: "Clear Requirements" |
| Missing checkpoints | Agents stop working | Schedule regular check-ins | Section: "PM Oversight" |
| Ignoring MCP tools | 5-10x slower, credit waste | Use MCP exclusively | Section: "MCP Enforcement" |

📖 **For detailed solutions, see:** `/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/tmux-bible.md`

## 🛠️ How It Works

### The Magic of Tmux
Tmux (terminal multiplexer) is the key enabler because:
- It persists terminal sessions even when disconnected
- Allows multiple windows/panes in one session
- Claude runs in the terminal, so it can control other Claude instances
- Commands can be sent programmatically to any window

### 💬 Simplified Agent Communication

We now use the `send-claude-message.sh` script for all agent communication:

```bash
# Send message to any Claude agent
./send-claude-message.sh session:window "Your message here"

# Examples:
./send-claude-message.sh frontend:0 "What's your progress on the login form?"
./send-claude-message.sh backend:1 "The API endpoint /api/users is returning 404"
./send-claude-message.sh project-manager:0 "Please coordinate with the QA team"
```

The script handles all timing complexities automatically, making agent communication reliable and consistent.

### Scheduling Check-ins
```bash
# Schedule with specific, actionable notes
./schedule_with_note.sh 30 "Review auth implementation, assign next task"
./schedule_with_note.sh 60 "Check test coverage, merge if passing"
./schedule_with_note.sh 120 "Full system check, rotate tasks if needed"
```

**Important**: The orchestrator needs to know which tmux window it's running in to schedule its own check-ins correctly. If scheduling isn't working, verify the orchestrator knows its current window with:
```bash
echo "Current window: $(tmux display-message -p "#{session_name}:#{window_index}")"
```

## 🎓 Advanced Usage

### Multi-Project Orchestration
```bash
# Start orchestrator
tmux new-session -s orchestrator

# Create project managers for each project
tmux new-window -n frontend-pm
tmux new-window -n backend-pm  
tmux new-window -n mobile-pm

# Each PM manages their own engineers
# Orchestrator coordinates between PMs
```

### Cross-Project Intelligence
The orchestrator can share insights between projects:
- "Frontend is using /api/v2/users, update backend accordingly"
- "Authentication is working in Project A, use same pattern in Project B"
- "Performance issue found in shared library, fix across all projects"

## 📚 Core Files

- **`tmux-bible.md`** - 🔴 **CRITICAL: Must-read lessons from expensive failures**
- `send-claude-message.sh` - Simplified agent communication script
- `schedule_with_note.sh` - Self-scheduling functionality
- `tmux_utils.py` - Tmux interaction utilities
- `CLAUDE.md` - Agent behavior instructions (includes tmux-bible references)
- `LEARNINGS.md` - Accumulated knowledge base
- `launch_orchestrator.sh` - Automated system startup with monitoring

## 🤝 Contributing & Optimization

The orchestrator evolves through community discoveries and optimizations. When contributing:

1. Document new tmux commands and patterns in CLAUDE.md
2. Share novel use cases and agent coordination strategies
3. Submit optimizations for claudes synchronization
4. Keep command reference up-to-date with latest findings
5. Test improvements across multiple sessions and scenarios

Key areas for enhancement:
- Agent communication patterns
- Cross-project coordination
- Novel automation workflows

## 📄 License

MIT License - Use freely but wisely. Remember: with great automation comes great responsibility.

---

*"The tools we build today will program themselves tomorrow"* - Alan Kay, 1971