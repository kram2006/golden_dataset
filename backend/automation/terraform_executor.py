"""Terraform execution wrapper with comprehensive logging"""
import os
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import shutil

logger = logging.getLogger(__name__)

class TerraformExecutor:
    """Execute Terraform commands and capture detailed logs"""
    
    def __init__(self, work_dir: Path):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if terraform is installed
        if not shutil.which('terraform'):
            logger.warning("Terraform not found in PATH")
    
    def write_main_tf(self, code: str) -> Path:
        """Write Terraform code to main.tf
        
        Args:
            code: Terraform code content
            
        Returns:
            Path to created main.tf file
        """
        main_tf_path = self.work_dir / "main.tf"
        main_tf_path.write_text(code)
        logger.info(f"Written main.tf to {main_tf_path}")
        return main_tf_path
    
    def _run_command(
        self,
        command: str,
        log_file: str,
        timeout: int = 300
    ) -> Dict:
        """Run a terraform command and capture output
        
        Args:
            command: Command to run (e.g., 'terraform init')
            log_file: Log file name
            timeout: Command timeout in seconds
            
        Returns:
            Dict with status, exit_code, execution_time, error_message
        """
        log_path = self.work_dir / log_file
        start_time = time.time()
        
        try:
            logger.info(f"Running: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            elapsed = time.time() - start_time
            
            # Write combined stdout and stderr to log file
            log_content = f"Command: {command}\n"
            log_content += f"Exit Code: {result.returncode}\n"
            log_content += f"Execution Time: {elapsed:.2f}s\n"
            log_content += "\n=== STDOUT ===\n"
            log_content += result.stdout
            log_content += "\n=== STDERR ===\n"
            log_content += result.stderr
            
            log_path.write_text(log_content)
            
            success = result.returncode == 0
            
            return {
                "status": "success" if success else "failed",
                "command": command,
                "exit_code": result.returncode,
                "execution_time_seconds": round(elapsed, 2),
                "error_message": result.stderr if not success else None,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            error_msg = f"Command timed out after {timeout}s"
            logger.error(error_msg)
            
            log_path.write_text(f"Command: {command}\nERROR: {error_msg}\n")
            
            return {
                "status": "failed",
                "command": command,
                "exit_code": -1,
                "execution_time_seconds": round(elapsed, 2),
                "error_message": error_msg
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            
            log_path.write_text(f"Command: {command}\nERROR: {error_msg}\n")
            
            return {
                "status": "failed",
                "command": command,
                "exit_code": -1,
                "execution_time_seconds": round(elapsed, 2),
                "error_message": error_msg
            }
    
    def init(self) -> Dict:
        """Run terraform init"""
        return self._run_command("terraform init", "init.log")
    
    def validate(self) -> Dict:
        """Run terraform validate"""
        return self._run_command("terraform validate", "validate.log")
    
    def plan(self) -> Dict:
        """Run terraform plan"""
        result = self._run_command(
            "terraform plan -out=tfplan",
            "plan.log",
            timeout=180
        )
        
        # Also create human-readable plan
        if result["exit_code"] == 0:
            readable = self._run_command(
                "terraform show tfplan",
                "plan_readable.txt",
                timeout=60
            )
            
            # Parse plan output for resource counts
            if readable["exit_code"] == 0:
                result["resources_to_create"] = self._count_resources(readable["stdout"], "create")
                result["resources_to_modify"] = self._count_resources(readable["stdout"], "update")
                result["resources_to_destroy"] = self._count_resources(readable["stdout"], "destroy")
        
        return result
    
    def apply(self) -> Dict:
        """Run terraform apply"""
        return self._run_command(
            "terraform apply -auto-approve tfplan",
            "apply.log",
            timeout=600  # 10 minutes for VM creation
        )
    
    def destroy(self) -> Dict:
        """Run terraform destroy"""
        return self._run_command(
            "terraform destroy -auto-approve",
            "destroy.log",
            timeout=300
        )
    
    def _count_resources(self, output: str, action: str) -> int:
        """Count resources in plan output
        
        Args:
            output: Terraform plan output
            action: Action type (create, update, destroy)
            
        Returns:
            Count of resources
        """
        import re
        
        # Look for patterns like "# resource will be created"
        if action == "create":
            pattern = r'will be created'
        elif action == "update":
            pattern = r'will be updated in-place'
        elif action == "destroy":
            pattern = r'will be destroyed'
        else:
            return 0
        
        matches = re.findall(pattern, output, re.IGNORECASE)
        return len(matches)
    
    def get_terraform_output(self) -> Dict:
        """Get terraform output values
        
        Returns:
            Dict of output values
        """
        result = self._run_command(
            "terraform output -json",
            "output.json",
            timeout=30
        )
        
        if result["exit_code"] == 0:
            try:
                import json
                return json.loads(result["stdout"])
            except json.JSONDecodeError:
                logger.error("Failed to parse terraform output JSON")
                return {}
        
        return {}
    
    def cleanup(self):
        """Clean up terraform state and plans"""
        files_to_remove = [
            "tfplan",
            ".terraform.lock.hcl"
        ]
        
        for file in files_to_remove:
            file_path = self.work_dir / file
            if file_path.exists():
                file_path.unlink()
        
        # Remove .terraform directory
        tf_dir = self.work_dir / ".terraform"
        if tf_dir.exists():
            shutil.rmtree(tf_dir)
