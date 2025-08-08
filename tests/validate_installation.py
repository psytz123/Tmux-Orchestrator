#!/usr/bin/env python3
"""
Validation test for Tmux Orchestrator installation
Checks that all components are properly installed and functional
"""

import sys
import os
from pathlib import Path
import subprocess
import json

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def print_status(message, status):
    """Print colored status message"""
    if status == "success":
        print(f"{GREEN}✅ {message}{NC}")
        return True
    elif status == "warning":
        print(f"{YELLOW}⚠️ {message}{NC}")
        return True
    else:
        print(f"{RED}❌ {message}{NC}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        return print_status(f"{description} exists", "success")
    else:
        return print_status(f"{description} missing at {filepath}", "fail")

def check_import(module_path, class_name, description):
    """Check if a Python module can be imported"""
    try:
        # Add to path
        sys.path.insert(0, str(Path(module_path).parent))
        module_name = Path(module_path).stem
        
        # Try to import
        module = __import__(module_name)
        if hasattr(module, class_name):
            return print_status(f"{description} can be imported", "success")
        else:
            return print_status(f"{description} missing class {class_name}", "fail")
    except Exception as e:
        return print_status(f"{description} import failed: {e}", "fail")

def check_script_executable(filepath, description):
    """Check if a script is executable"""
    if not Path(filepath).exists():
        return print_status(f"{description} not found", "fail")
    
    # Check if executable
    result = subprocess.run(['test', '-x', filepath], capture_output=True)
    if result.returncode == 0:
        return print_status(f"{description} is executable", "success")
    else:
        return print_status(f"{description} not executable (run chmod +x)", "warning")

def check_tmux_available():
    """Check if tmux is installed and available"""
    result = subprocess.run(['which', 'tmux'], capture_output=True)
    if result.returncode == 0:
        return print_status("tmux is installed", "success")
    else:
        return print_status("tmux not found - install tmux first", "fail")

def check_mcp_config():
    """Check if MCP configuration exists"""
    base_path = Path(__file__).parent.parent
    mcp_config = base_path / "mcp_config.json"
    
    if not mcp_config.exists():
        return print_status("MCP config not found", "warning")
    
    try:
        with open(mcp_config, 'r') as f:
            config = json.load(f)
            if 'mcpServers' in config:
                server_count = len(config['mcpServers'])
                return print_status(f"MCP config valid with {server_count} servers", "success")
            else:
                return print_status("MCP config missing mcpServers", "fail")
    except Exception as e:
        return print_status(f"MCP config invalid: {e}", "fail")

def check_claude_md_updates():
    """Check if CLAUDE.md has been updated with MCP protocols"""
    base_path = Path(__file__).parent.parent
    claude_md = base_path / "CLAUDE.md"
    
    if not claude_md.exists():
        return print_status("CLAUDE.md not found", "fail")
    
    with open(claude_md, 'r') as f:
        content = f.read()
        
    checks = [
        ("MCP-FIRST PROTOCOL", "MCP-first protocol"),
        ("Single-Task Protocol", "Single-task protocol"),
        ("Cross-Window Intelligence", "Cross-window monitoring"),
        ("Knowledge Graph Protocol", "Knowledge graph protocol")
    ]
    
    all_good = True
    for pattern, description in checks:
        if pattern in content:
            print_status(f"CLAUDE.md has {description}", "success")
        else:
            print_status(f"CLAUDE.md missing {description}", "fail")
            all_good = False
    
    return all_good

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("TMUX ORCHESTRATOR VALIDATION TEST")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    results = []
    
    print("\n📁 CHECKING DIRECTORY STRUCTURE")
    print("-" * 40)
    
    dirs = [
        "scripts", "monitoring", "templates", "core/orchestrator",
        "registry", "agents", "tests", "docs"
    ]
    
    for dir_name in dirs:
        dir_path = base_path / dir_name
        results.append(check_file_exists(dir_path, f"Directory: {dir_name}"))
    
    print("\n📄 CHECKING CRITICAL FILES")
    print("-" * 40)
    
    files = [
        ("CLAUDE.md", "CLAUDE.md instructions"),
        ("send-claude-message.sh", "Message sending script"),
        ("schedule_with_note.sh", "Scheduling script"),
        ("templates/agent_briefing_template.md", "Agent briefing template"),
        ("scripts/verify_mcp_usage.py", "MCP compliance monitor"),
        ("scripts/task_assigner.py", "Task assignment system"),
        ("scripts/activate_plan_mode.sh", "Plan mode activation"),
        ("scripts/auto_git_commit.sh", "Auto-commit system"),
        ("monitoring/cross_window_monitor.py", "Cross-window monitor"),
        ("core/orchestrator/agent_mcp_integration.py", "Agent-MCP integration"),
    ]
    
    for filepath, description in files:
        full_path = base_path / filepath
        results.append(check_file_exists(full_path, description))
    
    print("\n🔧 CHECKING SCRIPT PERMISSIONS")
    print("-" * 40)
    
    scripts = [
        ("scripts/verify_mcp_usage.py", "MCP monitor"),
        ("scripts/task_assigner.py", "Task assigner"),
        ("scripts/activate_plan_mode.sh", "Plan mode"),
        ("scripts/auto_git_commit.sh", "Auto-commit"),
        ("monitoring/cross_window_monitor.py", "Cross-window monitor"),
    ]
    
    for filepath, description in scripts:
        full_path = base_path / filepath
        results.append(check_script_executable(str(full_path), description))
    
    print("\n🐍 CHECKING PYTHON IMPORTS")
    print("-" * 40)
    
    # Test key imports
    sys.path.insert(0, str(base_path / "scripts"))
    sys.path.insert(0, str(base_path / "monitoring"))
    sys.path.insert(0, str(base_path / "core" / "orchestrator"))
    
    try:
        from verify_mcp_usage import MCPComplianceMonitor
        results.append(print_status("MCPComplianceMonitor imports", "success"))
    except:
        results.append(print_status("MCPComplianceMonitor import failed", "fail"))
    
    try:
        from task_assigner import TaskAssigner
        results.append(print_status("TaskAssigner imports", "success"))
    except:
        results.append(print_status("TaskAssigner import failed", "fail"))
    
    try:
        from cross_window_monitor import CrossWindowMonitor
        results.append(print_status("CrossWindowMonitor imports", "success"))
    except:
        results.append(print_status("CrossWindowMonitor import failed", "fail"))
    
    try:
        from agent_mcp_integration import AgentMCPOrchestrator
        results.append(print_status("AgentMCPOrchestrator imports", "success"))
    except:
        results.append(print_status("AgentMCPOrchestrator import failed", "fail"))
    
    print("\n⚙️ CHECKING SYSTEM REQUIREMENTS")
    print("-" * 40)
    
    results.append(check_tmux_available())
    results.append(check_mcp_config())
    
    print("\n📋 CHECKING CLAUDE.MD UPDATES")
    print("-" * 40)
    
    results.append(check_claude_md_updates())
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nTests Passed: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print(f"\n{GREEN}🎉 PERFECT! The Tmux Orchestrator is fully installed and configured!{NC}")
        print(f"{GREEN}You can now start using the orchestrator with your tmux sessions.{NC}")
    elif success_rate >= 80:
        print(f"\n{GREEN}✅ GOOD! The Tmux Orchestrator is mostly ready.{NC}")
        print(f"{YELLOW}Review the warnings above for optional improvements.{NC}")
    elif success_rate >= 60:
        print(f"\n{YELLOW}⚠️ PARTIAL SUCCESS. The core components are working.{NC}")
        print(f"{YELLOW}Fix the issues above for full functionality.{NC}")
    else:
        print(f"\n{RED}❌ INSTALLATION INCOMPLETE. Multiple components are missing.{NC}")
        print(f"{RED}Please review and fix the issues listed above.{NC}")
    
    print("\n" + "=" * 60)
    
    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())