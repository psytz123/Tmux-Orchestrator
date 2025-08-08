#!/usr/bin/env python3
"""
Cross-Window Intelligence Monitor
Monitors multiple tmux windows simultaneously for proactive error detection
Based on lesson: Orchestrator should catch errors before agents report them
"""

import subprocess
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class CrossWindowMonitor:
    def __init__(self):
        self.error_patterns = {
            # Python errors
            r'Error:': 'Generic error detected',
            r'Exception:': 'Exception raised',
            r'Traceback \(most recent call last\)': 'Python traceback detected',
            r'ModuleNotFoundError': 'Missing Python module',
            r'ImportError': 'Import error',
            r'AttributeError': 'Attribute error',
            r'TypeError': 'Type error',
            r'ValueError': 'Value error',
            r'KeyError': 'Key error',
            r'IndexError': 'Index error',
            r'FileNotFoundError': 'File not found',
            r'PermissionError': 'Permission denied',
            
            # Server/Port errors
            r'port \d+ is already in use': 'Port already in use',
            r'Address already in use': 'Address already in use',
            r'Connection refused': 'Connection refused',
            r'Connection timeout': 'Connection timeout',
            
            # Git errors
            r'fatal:': 'Git fatal error',
            r'merge conflict': 'Git merge conflict',
            r'not a git repository': 'Not a git repository',
            
            # Database errors
            r'SQLSTATE': 'SQL error',
            r'connection to database .* failed': 'Database connection failed',
            r'relation .* does not exist': 'Database table missing',
            
            # API errors
            r'404 Not Found': '404 error',
            r'500 Internal Server Error': '500 error',
            r'401 Unauthorized': 'Authentication error',
            r'403 Forbidden': 'Authorization error',
            
            # Test failures
            r'FAILED': 'Test failure',
            r'AssertionError': 'Assertion failed',
            r'\d+ failed, \d+ passed': 'Multiple test failures',
            
            # Performance issues
            r'took \d+\.\d+s': 'Slow operation detected',
            r'Memory limit exceeded': 'Memory issue',
            r'Maximum recursion depth exceeded': 'Recursion limit',
            
            # MCP specific
            r'mcp__.* not found': 'MCP tool not available',
            r'MCP server error': 'MCP server error',
        }
        
        self.solution_patterns = {
            'port \d+ is already in use': 'Try a different port or kill the process using: lsof -i :<port> and kill -9 <PID>',
            'ModuleNotFoundError|ImportError': 'Install missing module with pip or check virtual environment',
            'not a git repository': 'Initialize git with: git init',
            'connection to database .* failed': 'Check database is running and credentials are correct',
            '404 Not Found': 'Check the URL path and ensure the endpoint exists',
            'mcp__.* not found': 'Verify MCP tools are configured in mcp_config.json',
        }
        
        self.alerts_sent = {}  # Track alerts to avoid spam
        # Get script directory and navigate to project root
        script_dir = Path(__file__).parent.absolute()
        project_root = script_dir.parent
        self.log_file = project_root / "monitoring" / "alerts.log"
        
    def scan_window(self, session: str, window: int, lines: int = 100) -> List[Dict]:
        """Scan a specific window for issues"""
        issues = []
        
        try:
            # Capture recent output
            cmd = f"tmux capture-pane -t {session}:{window} -p -S -{lines}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            output = result.stdout
            
            # Check each error pattern
            for pattern, description in self.error_patterns.items():
                matches = re.findall(pattern, output, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Get context around error
                    context = self._get_error_context(output, pattern)
                    
                    # Check for solutions
                    solution = None
                    for sol_pattern, sol_text in self.solution_patterns.items():
                        if re.search(sol_pattern, pattern, re.IGNORECASE):
                            solution = sol_text
                            break
                    
                    issues.append({
                        'session': session,
                        'window': window,
                        'pattern': pattern,
                        'description': description,
                        'matches': len(matches),
                        'context': context,
                        'solution': solution,
                        'timestamp': datetime.now().isoformat()
                    })
            
        except Exception as e:
            print(f"Error scanning {session}:{window}: {e}")
        
        return issues
    
    def _get_error_context(self, output: str, pattern: str, context_lines: int = 3) -> str:
        """Get lines around error for context"""
        lines = output.split('\n')
        context = []
        
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Get surrounding lines
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context.extend(lines[start:end])
                break
        
        return '\n'.join(context[:10])  # Limit context size
    
    def scan_all_windows(self) -> Dict[str, List[Dict]]:
        """Scan all windows across all sessions for issues"""
        all_issues = {}
        
        try:
            # Get all sessions
            sessions_cmd = "tmux list-sessions -F '#{session_name}'"
            sessions_result = subprocess.run(sessions_cmd, shell=True, capture_output=True, text=True)
            
            if sessions_result.returncode != 0:
                return all_issues
            
            for session in sessions_result.stdout.strip().split('\n'):
                if not session:
                    continue
                
                # Get windows for this session
                windows_cmd = f"tmux list-windows -t {session} -F '#{{window_index}}:#{{window_name}}'"
                windows_result = subprocess.run(windows_cmd, shell=True, capture_output=True, text=True)
                
                if windows_result.returncode != 0:
                    continue
                
                for window_info in windows_result.stdout.strip().split('\n'):
                    if not window_info:
                        continue
                    
                    window_idx, window_name = window_info.split(':', 1) if ':' in window_info else (window_info, '')
                    
                    # Skip orchestrator/PM windows (they handle their own errors)
                    if any(skip in window_name.lower() for skip in ['orchestrator', 'pm', 'project-manager']):
                        continue
                    
                    # Scan for issues
                    issues = self.scan_window(session, int(window_idx))
                    
                    if issues:
                        key = f"{session}:{window_idx}"
                        all_issues[key] = issues
            
        except Exception as e:
            print(f"Error scanning all windows: {e}")
        
        return all_issues
    
    def alert_orchestrator(self, issues: Dict[str, List[Dict]]):
        """Send proactive alerts about detected issues"""
        if not issues:
            return
        
        for location, issue_list in issues.items():
            # Avoid alert spam - only alert once per issue per hour
            alert_key = f"{location}:{issue_list[0]['pattern']}"
            if alert_key in self.alerts_sent:
                last_alert = self.alerts_sent[alert_key]
                if (datetime.now() - last_alert).total_seconds() < 3600:
                    continue
            
            # Priority issues that need immediate attention
            priority_patterns = ['port .* in use', 'FAILED', 'fatal:', 'Traceback', 'mcp__.* not found']
            is_priority = any(p in issue_list[0]['pattern'] for p in priority_patterns)
            
            # Format alert message
            issue = issue_list[0]  # Report first issue
            alert = f"""
{'🚨 PRIORITY' if is_priority else '⚠️'} ISSUE DETECTED in {location}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue: {issue['description']}
Pattern: Found {issue['matches']} occurrence(s)
"""
            
            if issue['solution']:
                alert += f"Suggested Fix: {issue['solution']}\n"
            
            if issue['context']:
                alert += f"\nContext:\n{issue['context'][:200]}...\n"
            
            alert += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            # Send alert
            send_cmd = f"./send-claude-message.sh orchestrator:0 '{alert}'"
            subprocess.run(send_cmd, shell=True)
            
            # Log alert
            self.log_alert(location, issue)
            self.alerts_sent[alert_key] = datetime.now()
    
    def provide_assistance(self, agent: str, issue: Dict):
        """Provide proactive assistance to stuck agent"""
        if not issue['solution']:
            return
        
        assistance = f"""
📍 I detected an issue in your window:
{issue['description']}

Suggested solution:
{issue['solution']}

Let me know if you need help implementing this fix.
"""
        
        send_cmd = f"./send-claude-message.sh {agent} '{assistance}'"
        subprocess.run(send_cmd, shell=True)
    
    def log_alert(self, location: str, issue: Dict):
        """Log alerts to file for analysis"""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'location': location,
                'issue': issue['description'],
                'pattern': issue['pattern'],
                'solution': issue['solution']
            }
            
            # Append to log file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            print(f"Error logging alert: {e}")
    
    def generate_report(self) -> str:
        """Generate summary report of all issues"""
        issues = self.scan_all_windows()
        
        report = []
        report.append("=" * 80)
        report.append(f"CROSS-WINDOW INTELLIGENCE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        
        if not issues:
            report.append("\n✅ No issues detected across all windows\n")
        else:
            report.append(f"\n⚠️ Issues detected in {len(issues)} window(s):\n")
            
            # Group by severity
            critical = []
            warnings = []
            
            for location, issue_list in issues.items():
                for issue in issue_list:
                    if any(p in issue['pattern'] for p in ['fatal:', 'FAILED', 'Traceback']):
                        critical.append((location, issue))
                    else:
                        warnings.append((location, issue))
            
            if critical:
                report.append("\n🚨 CRITICAL ISSUES:")
                for location, issue in critical:
                    report.append(f"  - {location}: {issue['description']}")
                    if issue['solution']:
                        report.append(f"    Fix: {issue['solution']}")
            
            if warnings:
                report.append("\n⚠️ WARNINGS:")
                for location, issue in warnings[:10]:  # Limit to 10 warnings
                    report.append(f"  - {location}: {issue['description']}")
        
        report.append("\n" + "=" * 80)
        return '\n'.join(report)
    
    def monitor_continuously(self, interval: int = 30):
        """Run continuous monitoring"""
        print(f"Starting cross-window monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                issues = self.scan_all_windows()
                
                if issues:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found issues in {len(issues)} window(s)")
                    self.alert_orchestrator(issues)
                    
                    # Provide assistance to stuck agents
                    for location, issue_list in issues.items():
                        if issue_list and issue_list[0]['solution']:
                            self.provide_assistance(location, issue_list[0])
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] All clear")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cross-window intelligence monitor')
    parser.add_argument('--scan', nargs=2, metavar=('SESSION', 'WINDOW'), 
                       help='Scan specific window')
    parser.add_argument('--all', action='store_true', help='Scan all windows once')
    parser.add_argument('--monitor', action='store_true', help='Continuous monitoring')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Monitoring interval in seconds')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    args = parser.parse_args()
    
    monitor = CrossWindowMonitor()
    
    if args.scan:
        session, window = args.scan
        issues = monitor.scan_window(session, int(window))
        print(json.dumps(issues, indent=2))
    
    elif args.all:
        issues = monitor.scan_all_windows()
        print(json.dumps(issues, indent=2))
    
    elif args.monitor:
        monitor.monitor_continuously(args.interval)
    
    elif args.report:
        print(monitor.generate_report())
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()