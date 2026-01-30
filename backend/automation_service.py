"""Service for managing automation tasks"""
import os
import sys
import logging
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
import threading
from dotenv import load_dotenv, set_key

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from automation.orchestrator import GoldenDatasetOrchestrator
from automation.task_definitions import TASK_ORDER
from api_models import RunInfo, TaskStatus

logger = logging.getLogger(__name__)

class AutomationService:
    """Service for managing automation runs"""
    
    def __init__(self):
        self.runs: Dict[str, RunInfo] = {}
        self.active_threads: Dict[str, threading.Thread] = {}
        self.env_file = Path(__file__).parent / '.env'
        load_dotenv(self.env_file)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        return {
            'has_api_key': bool(api_key and api_key.strip()),
            'api_key_preview': f"{api_key[:8]}...{api_key[-4:]}" if api_key and len(api_key) > 12 else None,
            'xo_url': os.getenv('XO_URL', 'http://localhost:8080'),
            'xo_username': os.getenv('XO_USERNAME', 'admin@admin.net')
        }
    
    def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration in .env file"""
        try:
            if 'openrouter_api_key' in config and config['openrouter_api_key']:
                set_key(self.env_file, 'OPENROUTER_API_KEY', config['openrouter_api_key'])
                os.environ['OPENROUTER_API_KEY'] = config['openrouter_api_key']
                logger.info("Updated OpenRouter API key")
            
            if 'xo_url' in config and config['xo_url']:
                set_key(self.env_file, 'XO_URL', config['xo_url'])
                os.environ['XO_URL'] = config['xo_url']
            
            if 'xo_username' in config and config['xo_username']:
                set_key(self.env_file, 'XO_USERNAME', config['xo_username'])
                os.environ['XO_USERNAME'] = config['xo_username']
            
            if 'xo_password' in config and config['xo_password']:
                set_key(self.env_file, 'XO_PASSWORD', config['xo_password'])
                os.environ['XO_PASSWORD'] = config['xo_password']
            
            return {'success': True, 'message': 'Configuration updated successfully'}
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from OpenRouter API"""
        import requests
        
        try:
            response = requests.get('https://openrouter.ai/api/v1/models', timeout=10)
            response.raise_for_status()
            models_data = response.json()
            
            # Format models for frontend
            models = []
            for model in models_data.get('data', []):
                models.append({
                    'id': model.get('id', ''),
                    'name': model.get('name', model.get('id', '')),
                    'description': model.get('description', ''),
                    'context_length': model.get('context_length', 0),
                    'pricing': model.get('pricing', {})
                })
            
            return models
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            # Return some default models if API fails
            return [
                {'id': 'deepseek/deepseek-r1', 'name': 'DeepSeek R1', 'description': 'DeepSeek R1 model'},
                {'id': 'google/gemini-pro-1.5', 'name': 'Google Gemini Pro 1.5', 'description': 'Google Gemini Pro model'},
                {'id': 'anthropic/claude-3.5-sonnet', 'name': 'Claude 3.5 Sonnet', 'description': 'Anthropic Claude model'},
                {'id': 'openai/gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'OpenAI GPT-4 Turbo'},
            ]
    
    def start_automation(self, models: List[str], tasks: Optional[List[str]] = None, max_iterations: int = 20) -> str:
        """Start automation tasks in background"""
        run_id = str(uuid.uuid4())
        tasks_to_run = tasks or TASK_ORDER
        
        # Create run info
        run_info = RunInfo(
            run_id=run_id,
            status='pending',
            models=models,
            tasks=tasks_to_run,
            max_iterations=max_iterations,
            start_time=datetime.now(timezone.utc),
            total_tasks=len(models) * len(tasks_to_run)
        )
        
        self.runs[run_id] = run_info
        
        # Start background thread
        thread = threading.Thread(target=self._run_automation, args=(run_id, models, tasks_to_run, max_iterations))
        thread.daemon = True
        thread.start()
        
        self.active_threads[run_id] = thread
        
        logger.info(f"Started automation run {run_id}")
        return run_id
    
    def _run_automation(self, run_id: str, models: List[str], tasks: List[str], max_iterations: int):
        """Run automation in background thread"""
        try:
            self.runs[run_id].status = 'running'
            
            # Check API key
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key or not api_key.strip():
                raise ValueError("OpenRouter API key not configured")
            
            # Create orchestrator
            orchestrator = GoldenDatasetOrchestrator(
                base_dir=Path('/app/golden_dataset'),
                max_iterations=max_iterations,
                openrouter_api_key=api_key
            )
            
            # Map model IDs to short names for directory structure
            model_mapping = {}
            for i, model_id in enumerate(models):
                # Create a safe directory name from model ID
                safe_name = model_id.replace('/', '_').replace('.', '_')
                model_mapping[model_id] = safe_name
            
            # Update orchestrator models dynamically
            orchestrator.models = {}
            for model_id in models:
                short_name = model_mapping[model_id]
                orchestrator.models[short_name] = {
                    'full_name': model_id,
                    'api_id': model_id,
                    'short_name': short_name
                }
            
            # Run tasks
            results = orchestrator.run_all_tasks(
                models=list(orchestrator.models.keys()),
                tasks=tasks
            )
            
            # Update run status
            self.runs[run_id].status = 'completed'
            self.runs[run_id].end_time = datetime.now(timezone.utc)
            
            # Count successes/failures
            for model_results in results.values():
                for task_result in model_results.values():
                    if task_result.get('success', False):
                        self.runs[run_id].completed_tasks += 1
                    else:
                        self.runs[run_id].failed_tasks += 1
            
            logger.info(f"Automation run {run_id} completed")
            
        except Exception as e:
            logger.error(f"Automation run {run_id} failed: {e}")
            self.runs[run_id].status = 'failed'
            self.runs[run_id].end_time = datetime.now(timezone.utc)
        
        finally:
            # Clean up thread reference
            if run_id in self.active_threads:
                del self.active_threads[run_id]
    
    def get_run_status(self, run_id: str) -> Optional[RunInfo]:
        """Get status of a run"""
        return self.runs.get(run_id)
    
    def get_all_runs(self) -> List[RunInfo]:
        """Get all runs"""
        return list(self.runs.values())
    
    def cancel_run(self, run_id: str) -> bool:
        """Cancel a running automation"""
        if run_id in self.runs and self.runs[run_id].status == 'running':
            # Note: Graceful cancellation is complex, so we just mark it
            self.runs[run_id].status = 'cancelled'
            self.runs[run_id].end_time = datetime.now(timezone.utc)
            logger.info(f"Cancelled run {run_id}")
            return True
        return False
    
    def get_logs(self, lines: int = 100) -> List[str]:
        """Get recent log lines"""
        log_file = Path('/app/golden_dataset/logs/automation.log')
        if not log_file.exists():
            return []
        
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return []
    
    def get_datasets(self) -> List[Dict[str, Any]]:
        """Get list of generated datasets"""
        dataset_dir = Path('/app/golden_dataset/dataset')
        if not dataset_dir.exists():
            return []
        
        datasets = []
        for json_file in dataset_dir.rglob('*.json'):
            try:
                stat = json_file.stat()
                # Parse filename to extract info
                parts = json_file.stem.split('_')
                datasets.append({
                    'filename': json_file.name,
                    'path': str(json_file),
                    'model': json_file.parent.name,
                    'task_id': parts[0] if parts else 'unknown',
                    'size_bytes': stat.st_size,
                    'timestamp': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
                })
            except Exception as e:
                logger.error(f"Error processing dataset {json_file}: {e}")
        
        return sorted(datasets, key=lambda x: x['timestamp'], reverse=True)
    
    def get_screenshots(self) -> List[Dict[str, Any]]:
        """Get list of screenshots"""
        screenshot_dir = Path('/app/golden_dataset/screenshots')
        if not screenshot_dir.exists():
            return []
        
        screenshots = []
        for img_file in screenshot_dir.glob('*.png'):
            try:
                stat = img_file.stat()
                # Parse filename
                parts = img_file.stem.split('_')
                screenshots.append({
                    'filename': img_file.name,
                    'path': str(img_file),
                    'url': f'/api/screenshots/{img_file.name}',
                    'model': parts[1] if len(parts) > 1 else 'unknown',
                    'task_id': parts[0] if parts else 'unknown',
                    'type': '_'.join(parts[2:]) if len(parts) > 2 else 'screenshot'
                })
            except Exception as e:
                logger.error(f"Error processing screenshot {img_file}: {e}")
        
        return sorted(screenshots, key=lambda x: x['filename'])

# Global service instance
automation_service = AutomationService()
