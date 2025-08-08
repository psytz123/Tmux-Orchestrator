#!/usr/bin/env python3
"""
Agent-MCP Integration for Tmux Orchestrator
Incorporates advanced concepts from Agent-MCP project:
- Ephemeral agents with limited contexts
- Shared knowledge graph via mcp__memory
- File-level locking to prevent conflicts
- Semantic query-based memory retrieval
- Maximum agent limits with automatic cleanup
"""

import subprocess
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import hashlib

@dataclass
class EphemeralAgent:
    """Short-lived, focused agent with specific context"""
    id: str
    session: str
    window: int
    task: str
    context: str  # Limited, focused context
    created_at: datetime
    ttl_minutes: int = 30  # Time to live
    status: str = "active"
    locked_files: Set[str] = None

class AgentMCPOrchestrator:
    """
    Advanced orchestrator combining tmux management with MCP tools
    Based on Agent-MCP patterns for coordinated AI collaboration
    """
    
    def __init__(self):
        self.max_agents = 10  # Maximum concurrent agents
        self.active_agents: Dict[str, EphemeralAgent] = {}
        self.file_locks: Dict[str, str] = {}  # file_path -> agent_id
        self.knowledge_graph = MCPKnowledgeGraph()
        self.task_queue = []
        self.cleanup_interval = 300  # 5 minutes
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_agents)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
    
    def decompose_task(self, complex_task: str) -> List[Dict]:
        """
        Break complex task into linear, atomic sequences
        Each subtask is focused and can be handled by ephemeral agent
        """
        # Use MCP memory to check for similar past decompositions
        similar = self.knowledge_graph.semantic_query(f"task_decomposition:{complex_task}")
        
        if similar:
            return similar['subtasks']
        
        # Create atomic subtasks
        subtasks = []
        
        # Example decomposition patterns
        if "api" in complex_task.lower():
            subtasks.extend([
                {"type": "analysis", "task": "Analyze existing API structure", "mcp_tool": "mcp__filesystem"},
                {"type": "design", "task": "Design new endpoint schema", "mcp_tool": "mcp__fastapi"},
                {"type": "implement", "task": "Implement endpoint logic", "mcp_tool": "mcp__fastapi"},
                {"type": "test", "task": "Write and run tests", "mcp_tool": "mcp__pytest"},
                {"type": "document", "task": "Update API documentation", "mcp_tool": "mcp__memory"}
            ])
        elif "refactor" in complex_task.lower():
            subtasks.extend([
                {"type": "analysis", "task": "Identify refactoring targets", "mcp_tool": "mcp__filesystem"},
                {"type": "backup", "task": "Create safety branch", "mcp_tool": "mcp__git"},
                {"type": "refactor", "task": "Apply refactoring patterns", "mcp_tool": "mcp__filesystem"},
                {"type": "validate", "task": "Ensure tests pass", "mcp_tool": "mcp__pytest"}
            ])
        else:
            # Generic decomposition
            subtasks.append({
                "type": "generic",
                "task": complex_task,
                "mcp_tool": "mcp__filesystem"
            })
        
        # Store decomposition for future reference
        self.knowledge_graph.store(
            f"task_decomposition:{complex_task}",
            {"original": complex_task, "subtasks": subtasks}
        )
        
        return subtasks
    
    def spawn_ephemeral_agent(self, task: Dict) -> Optional[str]:
        """
        Create short-lived, focused agent for specific task
        Returns agent ID if successful
        """
        if len(self.active_agents) >= self.max_agents:
            self._cleanup_least_active_agent()
        
        # Generate unique agent ID
        agent_id = f"agent_{hashlib.md5(f'{task}{datetime.now()}'.encode()).hexdigest()[:8]}"
        
        # Find available tmux window
        session = self._find_or_create_session()
        window = self._create_agent_window(session, agent_id)
        
        if not window:
            return None
        
        # Create focused context for agent
        context = self._build_focused_context(task)
        
        # Create ephemeral agent
        agent = EphemeralAgent(
            id=agent_id,
            session=session,
            window=window,
            task=json.dumps(task),
            context=context,
            created_at=datetime.now(),
            locked_files=set()
        )
        
        # Start agent with limited context
        self._start_agent_with_context(agent)
        
        # Register agent
        self.active_agents[agent_id] = agent
        
        return agent_id
    
    def _build_focused_context(self, task: Dict) -> str:
        """Build limited, focused context for ephemeral agent"""
        context = f"""
You are an ephemeral agent with a specific, focused task.

TASK: {task['task']}
TYPE: {task['type']}
MCP_TOOL: {task['mcp_tool']}

CONTEXT LIMITATIONS:
- You exist only for this specific task
- Use ONLY the specified MCP tool
- Complete task and report results
- Your session will end after task completion

SHARED KNOWLEDGE:
"""
        # Add relevant knowledge from graph
        relevant = self.knowledge_graph.semantic_query(task['task'])
        if relevant:
            context += json.dumps(relevant, indent=2)
        
        return context
    
    def _start_agent_with_context(self, agent: EphemeralAgent):
        """Start agent with its focused context"""
        # Start Claude
        cmd = f"tmux send-keys -t {agent.session}:{agent.window} 'claude --dangerously-skip-permissions' Enter"
        subprocess.run(cmd, shell=True)
        time.sleep(5)
        
        # Send focused context
        message = agent.context.replace("'", "\\'")
        send_cmd = f"./send-claude-message.sh {agent.session}:{agent.window} '{message}'"
        subprocess.run(send_cmd, shell=True)
    
    def acquire_file_lock(self, agent_id: str, file_path: str) -> bool:
        """
        Acquire lock on file to prevent conflicts
        Returns True if lock acquired
        """
        if file_path in self.file_locks:
            return self.file_locks[file_path] == agent_id
        
        self.file_locks[file_path] = agent_id
        if agent_id in self.active_agents:
            self.active_agents[agent_id].locked_files.add(file_path)
        
        return True
    
    def release_file_lock(self, agent_id: str, file_path: str):
        """Release file lock"""
        if file_path in self.file_locks and self.file_locks[file_path] == agent_id:
            del self.file_locks[file_path]
            if agent_id in self.active_agents and file_path in self.active_agents[agent_id].locked_files:
                self.active_agents[agent_id].locked_files.remove(file_path)
    
    def coordinate_agents(self, agents: List[str]) -> Dict:
        """
        Coordinate multiple agents through shared knowledge graph
        Enables collaboration without direct communication
        """
        coordination_status = {}
        
        for agent_id in agents:
            if agent_id not in self.active_agents:
                continue
            
            agent = self.active_agents[agent_id]
            
            # Check agent progress
            progress = self._check_agent_progress(agent)
            
            # Share progress in knowledge graph
            self.knowledge_graph.store(
                f"agent_progress:{agent_id}",
                {
                    "task": agent.task,
                    "status": progress['status'],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            coordination_status[agent_id] = progress
        
        return coordination_status
    
    def _check_agent_progress(self, agent: EphemeralAgent) -> Dict:
        """Check agent's task progress"""
        try:
            # Capture agent output
            cmd = f"tmux capture-pane -t {agent.session}:{agent.window} -p -S -50"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = result.stdout.lower()
            
            # Check for completion indicators
            if any(word in output for word in ['completed', 'done', 'finished']):
                return {'status': 'completed', 'output': output[-500:]}
            elif any(word in output for word in ['error', 'failed', 'exception']):
                return {'status': 'error', 'output': output[-500:]}
            else:
                return {'status': 'in_progress', 'output': output[-200:]}
        except:
            return {'status': 'unknown'}
    
    def _cleanup_expired_agents(self):
        """Background thread to cleanup expired agents"""
        while True:
            time.sleep(self.cleanup_interval)
            
            now = datetime.now()
            expired = []
            
            for agent_id, agent in self.active_agents.items():
                if (now - agent.created_at).total_seconds() > agent.ttl_minutes * 60:
                    expired.append(agent_id)
            
            for agent_id in expired:
                self.terminate_agent(agent_id)
    
    def terminate_agent(self, agent_id: str):
        """Terminate ephemeral agent and cleanup resources"""
        if agent_id not in self.active_agents:
            return
        
        agent = self.active_agents[agent_id]
        
        # Release all file locks
        for file_path in list(agent.locked_files):
            self.release_file_lock(agent_id, file_path)
        
        # Store final state in knowledge graph
        final_output = self._check_agent_progress(agent)
        self.knowledge_graph.store(
            f"agent_final:{agent_id}",
            {
                "task": agent.task,
                "final_status": final_output['status'],
                "duration_minutes": (datetime.now() - agent.created_at).total_seconds() / 60,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Kill tmux window
        cmd = f"tmux kill-window -t {agent.session}:{agent.window}"
        subprocess.run(cmd, shell=True)
        
        # Remove from active agents
        del self.active_agents[agent_id]
    
    def _cleanup_least_active_agent(self):
        """Remove least recently active agent to make room"""
        if not self.active_agents:
            return
        
        # Find oldest agent
        oldest = min(self.active_agents.values(), key=lambda a: a.created_at)
        self.terminate_agent(oldest.id)
    
    def _find_or_create_session(self) -> str:
        """Find existing session or create new one"""
        # Try to use existing agent-pool session
        check_cmd = "tmux has-session -t agent-pool 2>/dev/null"
        if subprocess.run(check_cmd, shell=True).returncode == 0:
            return "agent-pool"
        
        # Create new session
        create_cmd = "tmux new-session -d -s agent-pool"
        subprocess.run(create_cmd, shell=True)
        return "agent-pool"
    
    def _create_agent_window(self, session: str, agent_id: str) -> Optional[int]:
        """Create new tmux window for agent"""
        try:
            # Get next window index
            cmd = f"tmux list-windows -t {session} -F '#{{window_index}}' | tail -1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout.strip():
                next_idx = int(result.stdout.strip()) + 1
            else:
                next_idx = 0
            
            # Create window
            create_cmd = f"tmux new-window -t {session}:{next_idx} -n '{agent_id}'"
            subprocess.run(create_cmd, shell=True)
            
            return next_idx
        except:
            return None


class MCPKnowledgeGraph:
    """
    Shared knowledge graph using mcp__memory
    Enables semantic queries and persistent context
    """
    
    def __init__(self):
        self.namespace = "orchestrator"
    
    def store(self, key: str, value: Dict):
        """Store knowledge in MCP memory"""
        # Simulate MCP memory storage
        # In real implementation, this would use mcp__memory.store()
        storage_cmd = f"echo 'mcp__memory.store(\"{key}\", {json.dumps(value)})' >> /tmp/mcp_memory_log"
        subprocess.run(storage_cmd, shell=True)
    
    def semantic_query(self, query: str) -> Optional[Dict]:
        """
        Perform semantic search in knowledge graph
        Returns most relevant stored knowledge
        """
        # Simulate MCP memory semantic search
        # In real implementation, this would use mcp__memory.search()
        
        # For now, return mock data based on query patterns
        if "task_decomposition" in query:
            return None  # Force new decomposition
        elif "api" in query.lower():
            return {
                "patterns": ["RESTful design", "FastAPI patterns"],
                "common_issues": ["Authentication", "Rate limiting"],
                "best_practices": ["Use Pydantic models", "Implement proper error handling"]
            }
        elif "refactor" in query.lower():
            return {
                "patterns": ["Extract method", "Replace conditional with polymorphism"],
                "tools": ["mcp__ast for code analysis"],
                "checklist": ["Ensure tests pass", "Preserve behavior", "Improve readability"]
            }
        
        return None
    
    def get_agent_history(self, agent_id: str) -> List[Dict]:
        """Get historical data for specific agent"""
        # In real implementation, query mcp__memory for agent history
        return []
    
    def get_task_patterns(self) -> Dict:
        """Retrieve successful task completion patterns"""
        # Analyze stored completions to identify patterns
        return {
            "successful_patterns": [],
            "failure_patterns": [],
            "optimization_opportunities": []
        }


def main():
    """Demonstration of Agent-MCP integration"""
    orchestrator = AgentMCPOrchestrator()
    
    # Example: Decompose and execute complex task
    complex_task = "Implement user authentication API with JWT tokens"
    
    print(f"Decomposing task: {complex_task}")
    subtasks = orchestrator.decompose_task(complex_task)
    
    print(f"Created {len(subtasks)} subtasks:")
    for i, task in enumerate(subtasks, 1):
        print(f"  {i}. {task['task']} (using {task['mcp_tool']})")
    
    # Spawn ephemeral agents for each subtask
    agent_ids = []
    for task in subtasks:
        agent_id = orchestrator.spawn_ephemeral_agent(task)
        if agent_id:
            print(f"Spawned agent {agent_id} for {task['type']}")
            agent_ids.append(agent_id)
    
    # Coordinate agents
    print("\nCoordinating agents...")
    time.sleep(10)
    status = orchestrator.coordinate_agents(agent_ids)
    
    print("\nAgent Status:")
    for agent_id, progress in status.items():
        print(f"  {agent_id}: {progress['status']}")

if __name__ == "__main__":
    main()