"""Memory manager for maintaining task-specific conversation history"""
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Manage conversation history for a single task execution"""
    
    def __init__(self, task_id: str, model_name: str, work_dir: Path):
        self.task_id = task_id
        self.model_name = model_name
        self.work_dir = Path(work_dir)
        self.messages: List[Dict[str, str]] = []
        self.iteration_count = 0
        
        self.memory_file = self.work_dir / "conversation_history.json"
    
    def add_system_message(self, content: str):
        """Add system message to conversation
        
        Args:
            content: System message content
        """
        self.messages.append({
            "role": "system",
            "content": content
        })
        self._save()
    
    def add_user_message(self, content: str):
        """Add user message to conversation
        
        Args:
            content: User message content
        """
        self.messages.append({
            "role": "user",
            "content": content
        })
        self._save()
    
    def add_assistant_message(self, content: str):
        """Add assistant message to conversation
        
        Args:
            content: Assistant message content
        """
        self.messages.append({
            "role": "assistant",
            "content": content
        })
        self._save()
    
    def add_error_feedback(self, error_type: str, error_message: str, logs: str):
        """Add terraform error feedback to conversation
        
        Args:
            error_type: Type of error (init, validate, plan, apply)
            error_message: Error message
            logs: Relevant log content
        """
        self.iteration_count += 1
        
        feedback = f"""The Terraform code from your previous response encountered an error during '{error_type}'.

Error Message:
{error_message}

Relevant Logs:
{logs[:2000]}  # Truncate to 2000 chars

Iteration: {self.iteration_count}

Please analyze the error and provide corrected Terraform code. Focus on:
1. Understanding why the error occurred
2. Fixing the specific issue
3. Ensuring the code uses the correct provider configuration and resource definitions
4. Making the code production-ready

Provide the complete corrected Terraform code."""
        
        self.add_user_message(feedback)
    
    def add_success_feedback(self, success_type: str):
        """Add success feedback
        
        Args:
            success_type: Type of success (init, validate, plan, apply)
        """
        feedback = f"The Terraform '{success_type}' succeeded! "
        
        if success_type == "apply":
            feedback += "The infrastructure has been successfully provisioned. Thank you!"
        else:
            feedback += f"Proceeding to the next step."
        
        self.add_user_message(feedback)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all conversation messages
        
        Returns:
            List of message dicts
        """
        return self.messages.copy()
    
    def get_iteration_count(self) -> int:
        """Get current iteration count
        
        Returns:
            Iteration count
        """
        return self.iteration_count
    
    def _save(self):
        """Save conversation to file"""
        try:
            data = {
                "task_id": self.task_id,
                "model_name": self.model_name,
                "iteration_count": self.iteration_count,
                "messages": self.messages,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self.memory_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save conversation memory: {e}")
    
    def load(self) -> bool:
        """Load conversation from file
        
        Returns:
            True if loaded successfully
        """
        if not self.memory_file.exists():
            return False
        
        try:
            data = json.loads(self.memory_file.read_text())
            self.messages = data.get("messages", [])
            self.iteration_count = data.get("iteration_count", 0)
            return True
        except Exception as e:
            logger.error(f"Failed to load conversation memory: {e}")
            return False
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
        self.iteration_count = 0
        if self.memory_file.exists():
            self.memory_file.unlink()
