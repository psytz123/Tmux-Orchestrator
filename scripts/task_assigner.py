#!/usr/bin/env python3
"""
Single-Task Assignment System
Ensures agents work on ONE task at a time with clear objectives and MCP tools
Based on lessons: Complex multi-step instructions confuse agents
"""

import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Task:
    """Single task specification"""
    id: str
    agent: str
    objective: str
    mcp_tool: str
    success_criteria: str
    time_limit: int  # minutes
    assigned_at: datetime
    status: str = "assigned"
    completed_at: Optional[datetime] = None
    result: Optional[str] = None

class TaskAssigner:
    def __init__(self):
        self.active_tasks = {}  # agent -> Task
        self.completed_tasks = []
        self.task_counter = 0
        # Get script directory and navigate to project root
        script_dir = Path(__file__).parent.absolute()
        project_root = script_dir.parent
        self.log_file = project_root / "registry" / "tasks.json"
        self.load_tasks()
        
    def load_tasks(self):
        """Load task history from file"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.task_counter = data.get('counter', 0)
                    self.completed_tasks = data.get('completed', [])
            except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
                print(f"Error loading tasks: {e}")
    
    def save_tasks(self):
        """Save task history to file"""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump({
                    'counter': self.task_counter,
                    'active': {k: asdict(v) for k, v in self.active_tasks.items()},
                    'completed': self.completed_tasks
                }, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def create_task(self, agent: str, task_spec: Dict) -> Task:
        """Create a new task with proper structure"""
        self.task_counter += 1
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d')}-{self.task_counter:04d}"
        
        task = Task(
            id=task_id,
            agent=agent,
            objective=task_spec['objective'],
            mcp_tool=task_spec.get('mcp_tool', 'mcp__filesystem'),
            success_criteria=task_spec['success_criteria'],
            time_limit=task_spec.get('time_limit', 15),
            assigned_at=datetime.now()
        )
        
        return task
    
    def assign_task(self, agent: str, task_spec: Dict) -> str:
        """
        Assign single task to agent with clear format
        Returns task ID
        """
        # Check if agent already has active task
        if agent in self.active_tasks:
            active = self.active_tasks[agent]
            if active.status == "assigned":
                return f"ERROR: Agent {agent} already has active task {active.id}"
        
        # Create task
        task = self.create_task(agent, task_spec)
        
        # Format message for agent
        message = self._format_task_message(task)
        
        # Send to agent via tmux
        send_cmd = f"./send-claude-message.sh {agent} '{message}'"
        result = subprocess.run(send_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            self.active_tasks[agent] = task
            self.save_tasks()
            print(f"✅ Assigned {task.id} to {agent}")
            return task.id
        else:
            return f"ERROR: Failed to send task to {agent}: {result.stderr}"
    
    def _format_task_message(self, task: Task) -> str:
        """Format task into clear message for agent"""
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {task.id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OBJECTIVE: {task.objective}

MCP TOOL: {task.mcp_tool}

SUCCESS CRITERIA: {task.success_criteria}

TIME LIMIT: {task.time_limit} minutes (deadline: {(task.assigned_at + timedelta(minutes=task.time_limit)).strftime('%H:%M:%S')})

INSTRUCTIONS:
1. Use ONLY the specified MCP tool
2. Complete the objective within time limit
3. Report completion with metrics
4. If blocked, report immediately with exact error

REMINDER: Using non-MCP tools will trigger a strike!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def check_task_status(self, agent: str) -> Dict:
        """Check if agent's task is complete or timed out"""
        if agent not in self.active_tasks:
            return {'status': 'no_task'}
        
        task = self.active_tasks[agent]
        elapsed = (datetime.now() - task.assigned_at).total_seconds() / 60
        
        if elapsed > task.time_limit:
            task.status = "timeout"
            return {
                'status': 'timeout',
                'task_id': task.id,
                'elapsed_minutes': round(elapsed, 1),
                'action': 'Issue strike and reassign'
            }
        
        # Check agent output for completion indicators
        try:
            cmd = f"tmux capture-pane -t {agent} -p -S -50"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = result.stdout.lower()
            
            # Look for completion indicators
            if any(indicator in output for indicator in ['completed', 'done', 'finished', 'success']):
                if task.id.lower() in output:
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    return {
                        'status': 'completed',
                        'task_id': task.id,
                        'elapsed_minutes': round(elapsed, 1)
                    }
            
            # Still in progress
            return {
                'status': 'in_progress',
                'task_id': task.id,
                'elapsed_minutes': round(elapsed, 1),
                'remaining_minutes': round(task.time_limit - elapsed, 1)
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def complete_task(self, agent: str, result: str = "Success"):
        """Mark task as complete and archive"""
        if agent in self.active_tasks:
            task = self.active_tasks[agent]
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result
            
            # Archive
            self.completed_tasks.append(asdict(task))
            del self.active_tasks[agent]
            self.save_tasks()
            
            print(f"✅ Task {task.id} completed by {agent}")
    
    def get_task_queue(self) -> List[Dict]:
        """Get list of ready-to-assign tasks from a queue file"""
        script_dir = Path(__file__).parent.absolute()
        project_root = script_dir.parent
        queue_file = project_root / "registry" / "task_queue.json"
        
        if queue_file.exists():
            try:
                with open(queue_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default tasks if no queue file
        return [
            {
                'objective': 'Verify all MCP tools are accessible',
                'mcp_tool': 'mcp__filesystem, mcp__git, mcp__memory',
                'success_criteria': 'List all available MCP tools and confirm they respond',
                'time_limit': 5
            },
            {
                'objective': 'Document current project structure',
                'mcp_tool': 'mcp__filesystem',
                'success_criteria': 'Create project map in mcp__memory',
                'time_limit': 10
            }
        ]
    
    def monitor_all_tasks(self) -> Dict:
        """Monitor all active tasks and return status"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'active_tasks': {},
            'alerts': []
        }
        
        for agent, task in self.active_tasks.items():
            status = self.check_task_status(agent)
            report['active_tasks'][agent] = {
                'task_id': task.id,
                'objective': task.objective,
                'status': status['status'],
                'elapsed': status.get('elapsed_minutes', 0)
            }
            
            # Generate alerts
            if status['status'] == 'timeout':
                report['alerts'].append(f"⚠️ {agent} exceeded time limit on {task.id}")
            elif status['status'] == 'completed':
                report['alerts'].append(f"✅ {agent} completed {task.id}")
        
        return report

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Single-task assignment system for agents')
    parser.add_argument('--assign', nargs=2, metavar=('AGENT', 'TASK_JSON'), 
                       help='Assign task to agent (e.g., session:0 \'{"objective":"..."}\')')
    parser.add_argument('--check', metavar='AGENT', help='Check task status for agent')
    parser.add_argument('--complete', metavar='AGENT', help='Mark task as complete')
    parser.add_argument('--monitor', action='store_true', help='Monitor all active tasks')
    parser.add_argument('--queue', action='store_true', help='Show task queue')
    
    args = parser.parse_args()
    
    assigner = TaskAssigner()
    
    if args.assign:
        agent, task_json = args.assign
        try:
            task_spec = json.loads(task_json)
            task_id = assigner.assign_task(agent, task_spec)
            print(f"Assigned: {task_id}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif args.check:
        status = assigner.check_task_status(args.check)
        print(json.dumps(status, indent=2))
    
    elif args.complete:
        assigner.complete_task(args.complete)
        print(f"Task completed for {args.complete}")
    
    elif args.monitor:
        report = assigner.monitor_all_tasks()
        print(json.dumps(report, indent=2))
        
        if report['alerts']:
            print("\nAlerts:")
            for alert in report['alerts']:
                print(f"  {alert}")
    
    elif args.queue:
        queue = assigner.get_task_queue()
        print("Task Queue:")
        for i, task in enumerate(queue, 1):
            print(f"\n{i}. {task['objective']}")
            print(f"   Tool: {task['mcp_tool']}")
            print(f"   Success: {task['success_criteria']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()