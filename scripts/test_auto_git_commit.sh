#!/bin/bash
#
# Test version of auto_git_commit.sh
# Runs one cycle immediately for testing
#

LOG_FILE="/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/monitoring/git_commits_test.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

test_commit_detection() {
    log_message "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_message "🧪 TESTING AUTO-COMMIT SYSTEM"
    log_message "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check for tmux sessions
    log_message ""
    log_message "📋 Checking tmux sessions..."
    
    if ! command -v tmux &> /dev/null; then
        log_message "❌ tmux not found"
        return 1
    fi
    
    sessions=$(tmux list-sessions -F '#{session_name}' 2>/dev/null)
    if [ -z "$sessions" ]; then
        log_message "❌ No tmux sessions found"
        return 1
    fi
    
    log_message "✅ Found sessions: $(echo $sessions | tr '\n' ' ')"
    
    # Check each session
    for session in $sessions; do
        log_message ""
        log_message "🔍 Checking session: $session"
        
        # Skip orchestrator
        if [[ "$session" == *"orchestrator"* ]] || [[ "$session" == *"orc"* ]]; then
            log_message "  ⏭️ Skipping (orchestrator session)"
            continue
        fi
        
        # Get windows
        windows=$(tmux list-windows -t "$session" -F '#{window_index}:#{window_name}' 2>/dev/null)
        
        for window_info in $windows; do
            IFS=':' read -r window_idx window_name <<< "$window_info"
            
            log_message "  Window $window_idx: $window_name"
            
            # Skip non-agent windows
            if [[ "$window_name" == *"server"* ]] || [[ "$window_name" == *"shell"* ]] || [[ "$window_name" == *"log"* ]]; then
                log_message "    ⏭️ Skipping (non-agent window)"
                continue
            fi
            
            # Get pane path
            pane_path=$(tmux display-message -t "${session}:${window_idx}" -p '#{pane_current_path}' 2>/dev/null)
            
            if [ -z "$pane_path" ]; then
                log_message "    ⚠️ Could not get pane path"
                continue
            fi
            
            log_message "    📁 Path: $pane_path"
            
            # Check if it's a git repo
            if [ -d "$pane_path/.git" ]; then
                log_message "    ✅ Git repository found"
                
                # Check for uncommitted changes
                cd "$pane_path" 2>/dev/null || continue
                
                if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
                    log_message "    ⚠️ Uncommitted changes detected!"
                    log_message "    Would commit: Auto-commit: $session:$window_idx @ $(date +%Y%m%d-%H%M%S)"
                else
                    log_message "    ✅ No changes to commit"
                fi
            else
                log_message "    ℹ️ Not a git repository"
            fi
        done
    done
    
    log_message ""
    log_message "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_message "✅ Test complete"
    log_message "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Test send-claude-message.sh availability
test_message_script() {
    log_message ""
    log_message "🔧 Testing send-claude-message.sh..."
    
    SCRIPT_PATH="/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/send-claude-message.sh"
    
    if [ -f "$SCRIPT_PATH" ]; then
        if [ -x "$SCRIPT_PATH" ]; then
            log_message "✅ send-claude-message.sh is executable"
        else
            log_message "⚠️ send-claude-message.sh exists but not executable"
            log_message "  Fix with: chmod +x '$SCRIPT_PATH'"
        fi
    else
        log_message "❌ send-claude-message.sh not found"
    fi
}

# Run tests
test_commit_detection
test_message_script

# Show summary
echo ""
echo "Test log saved to: $LOG_FILE"
echo ""
echo "To run the actual auto-commit system:"
echo "  ./scripts/auto_git_commit.sh 1800  # 30 minutes"
echo "  ./scripts/auto_git_commit.sh 60    # 1 minute (for testing)"
echo ""