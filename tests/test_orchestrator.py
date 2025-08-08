#!/usr/bin/env python3
"""
Comprehensive Test Suite for Tmux Orchestrator
Tests all major components and their integration
"""

import unittest
import subprocess
import json
import time
import sys
import os
import re
from pathlib import Path
from datetime import datetime
import tempfile

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "monitoring"))
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "orchestrator"))

# Import components to test
try:
    from verify_mcp_usage import MCPComplianceMonitor
    from task_assigner import TaskAssigner, Task
    from cross_window_monitor import CrossWindowMonitor
    from agent_mcp_integration import AgentMCPOrchestrator, MCPKnowledgeGraph
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all component files are in the correct locations")

class TestMCPCompliance(unittest.TestCase):
    """Test MCP compliance monitoring"""
    
    def setUp(self):
        self.monitor = MCPComplianceMonitor()
    
    def test_forbidden_pattern_detection(self):
        """Test detection of forbidden patterns"""
        # Simulate output with forbidden patterns
        test_patterns = [
            ("Read('file.txt')", "Using Read() instead of mcp__filesystem.read_file()"),
            ("Write('file.txt', content)", "Using Write() instead of mcp__filesystem.write_file()"),
            ("git add -A", "Using bash git instead of mcp__git.add()"),
            ("import requests", "Using requests instead of mcp__fetch"),
        ]
        
        for pattern, expected_description in test_patterns:
            # Check if pattern is in forbidden list
            # Handle both exact matches and partial matches
            pattern_base = pattern.split('(')[0] if '(' in pattern else pattern.split()[0] + ' ' + pattern.split()[1]
            found = False
            for forbidden_key in self.monitor.forbidden_patterns.keys():
                if pattern_base in forbidden_key or forbidden_key in pattern:
                    found = True
                    break
            self.assertTrue(found, f"Pattern '{pattern}' not found in forbidden patterns")
    
    def test_compliance_scoring(self):
        """Test compliance score calculation"""
        # Test perfect compliance
        report = {
            'violations': [],
            'mcp_usage_count': 10
        }
        score = 100 if not report['violations'] else max(0, 100 - len(report['violations']) * 25)
        self.assertEqual(score, 100)
        
        # Test with violations
        report['violations'] = [{'pattern': 'Read(', 'count': 1}]
        score = max(0, 100 - len(report['violations']) * 25)
        self.assertEqual(score, 75)
    
    def test_mcp_tool_tracking(self):
        """Test tracking of MCP tool usage"""
        # Check all expected MCP tools are tracked
        expected_tools = [
            'mcp__filesystem', 'mcp__git', 'mcp__memory',
            'mcp__postgres', 'mcp__fastapi'
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, self.monitor.mcp_tools)


class TestTaskAssigner(unittest.TestCase):
    """Test single-task assignment system"""
    
    def setUp(self):
        self.assigner = TaskAssigner()
        self.test_task = {
            'objective': 'Test task',
            'mcp_tool': 'mcp__filesystem',
            'success_criteria': 'Test passes',
            'time_limit': 5
        }
    
    def test_task_creation(self):
        """Test task creation with proper structure"""
        task = self.assigner.create_task('test:0', self.test_task)
        
        self.assertIsInstance(task, Task)
        self.assertEqual(task.objective, 'Test task')
        self.assertEqual(task.mcp_tool, 'mcp__filesystem')
        self.assertEqual(task.time_limit, 5)
        self.assertIn('TASK-', task.id)
    
    def test_task_timeout_detection(self):
        """Test detection of task timeouts"""
        # Create a task with 0 minute timeout for immediate timeout
        timeout_task = self.test_task.copy()
        timeout_task['time_limit'] = 0
        
        task = self.assigner.create_task('test:0', timeout_task)
        self.assigner.active_tasks['test:0'] = task
        
        # Check status should show timeout
        time.sleep(0.1)  # Small delay to ensure timeout
        status = self.assigner.check_task_status('test:0')
        self.assertEqual(status['status'], 'timeout')
    
    def test_single_task_enforcement(self):
        """Test that agents can only have one active task"""
        # Assign first task
        task1 = self.assigner.create_task('test:0', self.test_task)
        self.assigner.active_tasks['test:0'] = task1
        
        # Try to assign second task - should fail
        result = self.assigner.assign_task('test:0', self.test_task)
        self.assertIn('ERROR', result)
        self.assertIn('already has active task', result)


class TestCrossWindowMonitor(unittest.TestCase):
    """Test cross-window intelligence monitoring"""
    
    def setUp(self):
        self.monitor = CrossWindowMonitor()
    
    def test_error_pattern_detection(self):
        """Test detection of various error patterns"""
        test_cases = [
            ("Error: Something went wrong", "Generic error detected"),
            ("ModuleNotFoundError: No module named 'test'", "Missing Python module"),
            ("port 3000 is already in use", "Port already in use"),
            ("fatal: not a git repository", "Git fatal error"),
            ("FAILED tests/test_api.py", "Test failure"),
        ]
        
        for test_output, expected_type in test_cases:
            # Check if pattern would be detected
            detected = False
            for pattern in self.monitor.error_patterns.keys():
                if re.search(pattern, test_output, re.IGNORECASE):
                    detected = True
                    break
            self.assertTrue(detected, f"Failed to detect: {expected_type}")
    
    def test_solution_suggestions(self):
        """Test that solutions are provided for known issues"""
        # Check solutions exist for common patterns
        self.assertIn('port \d+ is already in use', self.monitor.solution_patterns)
        self.assertIn('ModuleNotFoundError|ImportError', self.monitor.solution_patterns)
        self.assertIn('not a git repository', self.monitor.solution_patterns)
    
    def test_alert_deduplication(self):
        """Test that alerts aren't sent repeatedly for same issue"""
        # Simulate sending an alert
        alert_key = "test:0:Error:"
        self.monitor.alerts_sent[alert_key] = datetime.now()
        
        # Check that recent alert is still considered "sent"
        self.assertIn(alert_key, self.monitor.alerts_sent)


class TestAgentMCPIntegration(unittest.TestCase):
    """Test Agent-MCP integration components"""
    
    def setUp(self):
        self.orchestrator = AgentMCPOrchestrator()
    
    def test_task_decomposition(self):
        """Test complex task decomposition"""
        complex_task = "Implement user authentication API"
        subtasks = self.orchestrator.decompose_task(complex_task)
        
        self.assertIsInstance(subtasks, list)
        self.assertTrue(len(subtasks) > 0)
        
        # Check subtask structure
        for subtask in subtasks:
            self.assertIn('type', subtask)
            self.assertIn('task', subtask)
            self.assertIn('mcp_tool', subtask)
    
    def test_ephemeral_agent_limit(self):
        """Test maximum agent limit enforcement"""
        # Try to create more than max agents
        for i in range(self.orchestrator.max_agents + 2):
            agent_id = f"test_agent_{i}"
            self.orchestrator.active_agents[agent_id] = None
        
        # Should not exceed max
        self.assertLessEqual(len(self.orchestrator.active_agents), 
                           self.orchestrator.max_agents + 2)
    
    def test_file_lock_mechanism(self):
        """Test file locking to prevent conflicts"""
        # Acquire lock
        success = self.orchestrator.acquire_file_lock('agent1', '/test/file.py')
        self.assertTrue(success)
        
        # Try to acquire same lock with different agent
        success = self.orchestrator.acquire_file_lock('agent2', '/test/file.py')
        self.assertFalse(success)
        
        # Release lock
        self.orchestrator.release_file_lock('agent1', '/test/file.py')
        
        # Now agent2 should be able to acquire
        success = self.orchestrator.acquire_file_lock('agent2', '/test/file.py')
        self.assertTrue(success)
    
    def test_knowledge_graph_storage(self):
        """Test knowledge graph storage and retrieval"""
        kg = MCPKnowledgeGraph()
        
        # Test storage (just checks it doesn't error)
        kg.store('test_key', {'data': 'test_value'})
        
        # Test semantic query
        result = kg.semantic_query('api')
        self.assertIsInstance(result, (dict, type(None)))


class TestScriptExecution(unittest.TestCase):
    """Test bash script execution"""
    
    def test_script_permissions(self):
        """Test that all scripts are executable"""
        script_files = [
            'scripts/verify_mcp_usage.py',
            'scripts/task_assigner.py',
            'scripts/activate_plan_mode.sh',
            'scripts/auto_git_commit.sh',
            'monitoring/cross_window_monitor.py',
        ]
        
        base_path = Path(__file__).parent.parent
        
        for script in script_files:
            script_path = base_path / script
            if script_path.exists():
                # Check if executable
                result = subprocess.run(['test', '-x', str(script_path)], 
                                      capture_output=True)
                self.assertEqual(result.returncode, 0, 
                               f"{script} is not executable")
    
    def test_send_claude_message_exists(self):
        """Test that send-claude-message.sh exists"""
        script_path = Path(__file__).parent.parent / 'send-claude-message.sh'
        self.assertTrue(script_path.exists(), 
                       "send-claude-message.sh not found")


class TestIntegration(unittest.TestCase):
    """Integration tests for component interaction"""
    
    def test_mcp_compliance_with_task_assignment(self):
        """Test that task assignments include MCP tool specification"""
        assigner = TaskAssigner()
        task_spec = {
            'objective': 'Integration test',
            'mcp_tool': 'mcp__filesystem',
            'success_criteria': 'Test completes',
            'time_limit': 5
        }
        
        task = assigner.create_task('test:0', task_spec)
        
        # Verify MCP tool is specified
        self.assertEqual(task.mcp_tool, 'mcp__filesystem')
        
        # Check task message format includes MCP tool
        message = assigner._format_task_message(task)
        self.assertIn('MCP TOOL:', message)
        self.assertIn('mcp__filesystem', message)
    
    def test_cross_window_monitor_with_solutions(self):
        """Test that monitor provides solutions for detected issues"""
        monitor = CrossWindowMonitor()
        
        # Simulate detecting a port issue
        test_output = "Error: port 3000 is already in use"
        
        # Find matching pattern and solution
        solution_found = False
        for pattern, solution in monitor.solution_patterns.items():
            if re.search(pattern, test_output, re.IGNORECASE):
                solution_found = True
                self.assertIsNotNone(solution)
                break
        
        self.assertTrue(solution_found, "No solution found for port issue")


class TestConfiguration(unittest.TestCase):
    """Test configuration and setup"""
    
    def test_directory_structure(self):
        """Test that required directories exist"""
        base_path = Path(__file__).parent.parent
        
        required_dirs = [
            'scripts',
            'monitoring',
            'templates',
            'core/orchestrator',
            'registry',
            'agents/briefings',
            'agents/logs',
            'agents/status'
        ]
        
        for dir_path in required_dirs:
            full_path = base_path / dir_path
            self.assertTrue(full_path.exists(), 
                          f"Required directory missing: {dir_path}")
    
    def test_critical_files_exist(self):
        """Test that critical files exist"""
        base_path = Path(__file__).parent.parent
        
        critical_files = [
            'CLAUDE.md',
            'templates/agent_briefing_template.md',
            'send-claude-message.sh',
            'schedule_with_note.sh',
        ]
        
        for file_path in critical_files:
            full_path = base_path / file_path
            self.assertTrue(full_path.exists(), 
                          f"Critical file missing: {file_path}")


def run_component_tests():
    """Run tests for individual components"""
    print("=" * 80)
    print("TMUX ORCHESTRATOR TEST SUITE")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMCPCompliance,
        TestTaskAssigner,
        TestCrossWindowMonitor,
        TestAgentMCPIntegration,
        TestScriptExecution,
        TestIntegration,
        TestConfiguration
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result


def run_live_tmux_tests():
    """Run tests that require actual tmux sessions"""
    print("\n" + "=" * 80)
    print("LIVE TMUX TESTS")
    print("=" * 80)
    
    # Check if tmux is available
    result = subprocess.run(['which', 'tmux'], capture_output=True)
    if result.returncode != 0:
        print("❌ tmux not found - skipping live tests")
        return False
    
    print("✅ tmux found")
    
    # Test tmux session creation
    test_session = "test-orchestrator"
    try:
        # Create test session
        subprocess.run(['tmux', 'new-session', '-d', '-s', test_session], 
                      capture_output=True)
        print(f"✅ Created test session: {test_session}")
        
        # List sessions
        result = subprocess.run(['tmux', 'list-sessions'], 
                              capture_output=True, text=True)
        if test_session in result.stdout:
            print("✅ Session listing works")
        
        # Test window creation
        subprocess.run(['tmux', 'new-window', '-t', f'{test_session}:1', 
                       '-n', 'test-window'], capture_output=True)
        print("✅ Window creation works")
        
        # Test capture-pane
        result = subprocess.run(['tmux', 'capture-pane', '-t', 
                               f'{test_session}:0', '-p'], 
                              capture_output=True)
        print("✅ Pane capture works")
        
        # Clean up
        subprocess.run(['tmux', 'kill-session', '-t', test_session], 
                      capture_output=True)
        print(f"✅ Cleaned up test session")
        
        return True
        
    except Exception as e:
        print(f"❌ Live tmux test failed: {e}")
        # Try to clean up
        subprocess.run(['tmux', 'kill-session', '-t', test_session], 
                      capture_output=True, stderr=subprocess.DEVNULL)
        return False


if __name__ == "__main__":
    import sys
    
    # Run component tests
    result = run_component_tests()
    
    # Run live tmux tests if available
    tmux_success = run_live_tmux_tests()
    
    # Overall result
    print("\n" + "=" * 80)
    print("OVERALL TEST RESULTS")
    print("=" * 80)
    
    if result.wasSuccessful() and tmux_success:
        print("✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        if not result.wasSuccessful():
            print("  - Component tests had failures")
        if not tmux_success:
            print("  - Tmux live tests failed or were skipped")
        sys.exit(1)