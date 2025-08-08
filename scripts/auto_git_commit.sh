#!/bin/bash
#
# Automated Git Commit System
# Commits all agent work every 30 minutes to prevent work loss
# Based on critical lesson: V1 lost hours of work due to no commits
#

COMMIT_INTERVAL=${1:-1800}  # Default 30 minutes (1800 seconds)
LOG_FILE="/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/monitoring/git_commits.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

commit_project() {
    local session=$1
    local window=$2
    local project_path=$3
    
    if [ ! -d "$project_path/.git" ]; then
        log_message "⚠️ Not a git repository: $project_path"
        return 1
    fi
    
    # Check if there are changes to commit
    cd "$project_path" || return 1
    if [ -z "$(git status --porcelain)" ]; then
        log_message "No changes in $session:$window ($project_path)"
        return 0
    fi
    
    # Get current branch
    BRANCH=$(git branch --show-current)
    
    # Create auto-commit message with context
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    MESSAGE="Auto-commit: $session:$window @ $TIMESTAMP"
    
    # Try MCP git first (preferred)
    MCP_CMD="mcp__git.add_all() && mcp__git.commit('$MESSAGE')"
    
    # Send MCP git commands to agent
    log_message "📝 Auto-committing $session:$window via MCP"
    ./send-claude-message.sh ${session}:${window} "$MCP_CMD"
    
    # Wait for MCP command to execute
    sleep 5
    
    # Verify commit happened
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null)
    
    # If MCP failed, fall back to direct git
    if [[ ! "$LAST_COMMIT" == *"$TIMESTAMP"* ]]; then
        log_message "MCP git failed, using direct git for $session:$window"
        
        # Direct git commit
        git add -A
        git commit -m "$MESSAGE" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            log_message "✅ Direct commit successful: $session:$window on branch $BRANCH"
        else
            log_message "❌ Commit failed for $session:$window"
            return 1
        fi
    else
        log_message "✅ MCP commit successful: $session:$window on branch $BRANCH"
    fi
    
    # Tag stable versions every 6 commits
    COMMIT_COUNT=$(git rev-list --count HEAD)
    if [ $((COMMIT_COUNT % 6)) -eq 0 ]; then
        TAG="stable-auto-$TIMESTAMP"
        git tag "$TAG"
        log_message "🏷️ Tagged stable version: $TAG"
    fi
    
    return 0
}

perform_commit_cycle() {
    log_message "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_message "🔄 Starting auto-commit cycle"
    
    local commit_count=0
    local error_count=0
    
    # Get all active sessions
    for session in $(tmux list-sessions -F '#{session_name}' 2>/dev/null); do
        # Skip orchestrator session
        if [[ "$session" == *"orchestrator"* ]] || [[ "$session" == *"orc"* ]]; then
            continue
        fi
        
        # Get windows for this session
        for window_info in $(tmux list-windows -t "$session" -F '#{window_index}:#{window_name}:#{pane_current_path}' 2>/dev/null); do
            IFS=':' read -r window_idx window_name project_path <<< "$window_info"
            
            # Skip non-agent windows
            if [[ "$window_name" == *"server"* ]] || [[ "$window_name" == *"shell"* ]] || [[ "$window_name" == *"log"* ]]; then
                continue
            fi
            
            # Attempt commit
            if commit_project "$session" "$window_idx" "$project_path"; then
                ((commit_count++))
            else
                ((error_count++))
            fi
        done
    done
    
    log_message "📊 Commit cycle complete: $commit_count successful, $error_count failed"
    
    # Alert if too many failures
    if [ $error_count -gt 3 ]; then
        ALERT="⚠️ AUTO-COMMIT ALERT: $error_count commits failed! Check git status in affected projects."
        ./send-claude-message.sh orchestrator:0 "$ALERT" 2>/dev/null || true
    fi
    
    log_message "⏰ Next auto-commit in $((COMMIT_INTERVAL/60)) minutes"
    log_message "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Handle script termination
cleanup() {
    log_message "🛑 Auto-commit system stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main loop
log_message "🚀 Auto-commit system started (interval: $((COMMIT_INTERVAL/60)) minutes)"
log_message "Press Ctrl+C to stop"

while true; do
    perform_commit_cycle
    sleep "$COMMIT_INTERVAL"
done