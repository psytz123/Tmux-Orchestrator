#!/usr/bin/env python3
"""
MCP Compliance Monitor - Tracks agent MCP tool usage and violations
Enforces MCP-only policy based on lessons from V1/V2 failures
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path

class MCPComplianceMonitor:
    def __init__(self):
        self.compliance_scores = {}
        self.violation_history = {}
        self.mcp_tools = [
            'mcp__filesystem', 'mcp__git', 'mcp__memory',
            'mcp__postgres', 'mcp__sqlite',
            'mcp__fastapi', 'mcp__streamlit', 'mcp__sqlalchemy',
            'mcp__scikit-learn', 'mcp__pandas', 'mcp__numpy',
            'mcp__huggingface-transformers', 'mcp__tensorflow', 'mcp__pytorch',
            'mcp__fetch', 'mcp__browser'
        ]
        self.forbidden_patterns = {
            'Read(': "Using Read() instead of mcp__filesystem.read_file()",
            'Write(': "Using Write() instead of mcp__filesystem.write_file()",
            'MultiEdit(': "Using MultiEdit() instead of mcp__filesystem operations",
            'git add': "Using bash git instead of mcp__git.add()",
            'git commit': "Using bash git instead of mcp__git.commit()",
            'git push': "Using bash git instead of mcp__git.push()",
            'git status': "Using bash git instead of mcp__git.status()",
            'import requests': "Using requests instead of mcp__fetch",
            'open(': "Using Python open() instead of mcp__filesystem",
            'with open': "Using Python file operations instead of mcp__filesystem",
            'subprocess.run': "Using subprocess for git instead of mcp__git",
            'os.system': "Using os.system instead of MCP tools",
        }
        
    def check_agent_mcp_usage(self, session: str, window: int) -> Dict:
        """
        Verify agent is using MCP tools exclusively
        Returns compliance report with score and violations
        """
        try:
            # Capture last 1000 lines of agent activity
            cmd = f"tmux capture-pane -t {session}:{window} -p -S -1000"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'error': f"Failed to capture pane: {result.stderr}",
                    'session': session,
                    'window': window
                }
            
            output = result.stdout
            
            # Check for violations
            violations = []
            for pattern, description in self.forbidden_patterns.items():
                if pattern in output:
                    count = output.count(pattern)
                    violations.append({
                        'pattern': pattern,
                        'description': description,
                        'count': count
                    })
            
            # Check for good MCP usage
            mcp_usage_count = 0
            mcp_tools_used = []
            for tool in self.mcp_tools:
                if tool in output:
                    count = output.count(tool)
                    mcp_usage_count += count
                    mcp_tools_used.append({'tool': tool, 'count': count})
            
            # Calculate compliance score
            if violations:
                # Each violation reduces score by 25%, minimum 0
                score = max(0, 100 - (len(violations) * 25))
            elif mcp_usage_count == 0:
                # No MCP usage and no violations = suspicious
                score = 50
            else:
                # Good MCP usage, no violations
                score = 100
            
            # Store history
            agent_id = f"{session}:{window}"
            if agent_id not in self.compliance_scores:
                self.compliance_scores[agent_id] = []
            self.compliance_scores[agent_id].append(score)
            
            if agent_id not in self.violation_history:
                self.violation_history[agent_id] = []
            self.violation_history[agent_id].extend(violations)
            
            report = {
                'session': session,
                'window': window,
                'timestamp': datetime.now().isoformat(),
                'compliance_score': score,
                'violations': violations,
                'mcp_usage_count': mcp_usage_count,
                'mcp_tools_used': mcp_tools_used,
                'recommendation': self._get_recommendation(score, violations)
            }
            
            return report
            
        except Exception as e:
            return {
                'error': str(e),
                'session': session,
                'window': window
            }
    
    def _get_recommendation(self, score: int, violations: List[Dict]) -> str:
        """Generate recommendation based on compliance score"""
        if score == 100:
            return "Excellent - Continue current practices"
        elif score >= 75:
            return "Good - Minor improvements needed"
        elif score >= 50:
            return "Warning - Immediate correction required"
        else:
            return "Critical - Consider agent replacement"
    
    def check_all_agents(self) -> List[Dict]:
        """Check compliance for all active agents"""
        reports = []
        
        try:
            # Get all sessions
            sessions_cmd = "tmux list-sessions -F '#{session_name}'"
            sessions_result = subprocess.run(sessions_cmd, shell=True, capture_output=True, text=True)
            
            if sessions_result.returncode != 0:
                return [{'error': 'No tmux sessions found'}]
            
            for session in sessions_result.stdout.strip().split('\n'):
                if not session or 'orchestrator' in session.lower():
                    continue
                
                # Get windows for this session
                windows_cmd = f"tmux list-windows -t {session} -F '#{{window_index}}:#{{window_name}}'"
                windows_result = subprocess.run(windows_cmd, shell=True, capture_output=True, text=True)
                
                if windows_result.returncode == 0:
                    for window_info in windows_result.stdout.strip().split('\n'):
                        if not window_info:
                            continue
                        
                        window_idx = window_info.split(':')[0]
                        window_name = window_info.split(':', 1)[1] if ':' in window_info else ''
                        
                        # Skip non-agent windows
                        if any(skip in window_name.lower() for skip in ['server', 'shell', 'log']):
                            continue
                        
                        report = self.check_agent_mcp_usage(session, int(window_idx))
                        reports.append(report)
            
        except Exception as e:
            reports.append({'error': str(e)})
        
        return reports
    
    def generate_compliance_report(self) -> str:
        """Generate a formatted compliance report for all agents"""
        reports = self.check_all_agents()
        
        output = []
        output.append("=" * 80)
        output.append(f"MCP COMPLIANCE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 80)
        output.append("")
        
        for report in reports:
            if 'error' in report:
                output.append(f"ERROR: {report['error']}")
                continue
            
            agent = f"{report['session']}:{report['window']}"
            score = report['compliance_score']
            
            # Score indicator
            if score == 100:
                indicator = "✅"
            elif score >= 75:
                indicator = "⚠️"
            elif score >= 50:
                indicator = "⚠️⚠️"
            else:
                indicator = "🚨"
            
            output.append(f"{indicator} Agent: {agent}")
            output.append(f"   Compliance Score: {score}%")
            
            if report['violations']:
                output.append("   Violations:")
                for v in report['violations']:
                    output.append(f"   - {v['description']} (found {v['count']} times)")
            
            if report['mcp_tools_used']:
                output.append("   MCP Tools Used:")
                for tool in report['mcp_tools_used']:
                    output.append(f"   + {tool['tool']} ({tool['count']} calls)")
            
            output.append(f"   Recommendation: {report['recommendation']}")
            output.append("")
        
        return '\n'.join(output)
    
    def alert_violations(self, report: Dict) -> None:
        """Send alert for violations to orchestrator"""
        if report['compliance_score'] < 75:
            agent = f"{report['session']}:{report['window']}"
            
            message = f"⚠️ MCP VIOLATION ALERT - {agent}\n"
            message += f"Score: {report['compliance_score']}%\n"
            
            if report['violations']:
                message += "Violations:\n"
                for v in report['violations'][:3]:  # Top 3 violations
                    message += f"- {v['description']}\n"
            
            message += f"Action: {report['recommendation']}"
            
            # Send to orchestrator
            send_cmd = f"./send-claude-message.sh orchestrator:0 '{message}'"
            subprocess.run(send_cmd, shell=True)

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor MCP compliance for tmux agents')
    parser.add_argument('--session', help='Specific session to check')
    parser.add_argument('--window', type=int, help='Specific window to check')
    parser.add_argument('--all', action='store_true', help='Check all agents')
    parser.add_argument('--watch', action='store_true', help='Continuous monitoring')
    parser.add_argument('--interval', type=int, default=120, help='Watch interval in seconds')
    
    args = parser.parse_args()
    
    monitor = MCPComplianceMonitor()
    
    if args.watch:
        print(f"Starting continuous monitoring (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print("\n" + "=" * 80)
                print(f"Check at {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 80)
                
                if args.session and args.window is not None:
                    report = monitor.check_agent_mcp_usage(args.session, args.window)
                    print(json.dumps(report, indent=2))
                    monitor.alert_violations(report)
                else:
                    print(monitor.generate_compliance_report())
                    for report in monitor.check_all_agents():
                        if 'error' not in report:
                            monitor.alert_violations(report)
                
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    
    elif args.all:
        print(monitor.generate_compliance_report())
    
    elif args.session and args.window is not None:
        report = monitor.check_agent_mcp_usage(args.session, args.window)
        print(json.dumps(report, indent=2))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()