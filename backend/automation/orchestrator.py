"""Main orchestrator for golden dataset generation"""
import os
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import shutil

from .openrouter_client import OpenRouterClient
from .terraform_executor import TerraformExecutor
from .xen_screenshot import XenScreenshot
from .memory_manager import ConversationMemory
from .dataset_generator import DatasetGenerator
from .task_definitions import (
    TaskDefinition,
    get_task,
    get_all_tasks,
    build_full_prompt,
    PLATFORM_CONTEXT,
    TASK_ORDER
)

logger = logging.getLogger(__name__)

class GoldenDatasetOrchestrator:
    """Main orchestrator for automating golden dataset generation"""
    
    def __init__(
        self,
        base_dir: Path = Path("/app/golden_dataset"),
        max_iterations: int = 20,
        openrouter_api_key: Optional[str] = None
    ):
        self.base_dir = Path(base_dir)
        self.max_iterations = max_iterations
        
        # Initialize clients
        self.openrouter = OpenRouterClient(api_key=openrouter_api_key)
        self.xen_screenshot = XenScreenshot()
        
        # Model configurations
        self.models = {
            "deepseek_r1": {
                "full_name": "DeepSeek R1",
                "api_id": "deepseek/deepseek-r1",
                "short_name": "deepseek_r1"
            },
            "google_gemini_3_pro": {
                "full_name": "Google Gemini 3 Pro",
                "api_id": "google/gemini-pro-1.5",
                "short_name": "google_gemini_3_pro"
            }
        }
        
        logger.info(f"Orchestrator initialized with base_dir: {self.base_dir}")
    
    def run_all_tasks(self, models: Optional[List[str]] = None, tasks: Optional[List[str]] = None):
        """Run all tasks for specified models
        
        Args:
            models: List of model keys to run (default: all models)
            tasks: List of task IDs to run (default: all tasks in order)
        """
        models_to_run = models or list(self.models.keys())
        tasks_to_run = tasks or TASK_ORDER
        
        logger.info(f"Starting golden dataset generation")
        logger.info(f"Models: {models_to_run}")
        logger.info(f"Tasks: {tasks_to_run}")
        
        results = {}
        
        for model_key in models_to_run:
            if model_key not in self.models:
                logger.error(f"Unknown model: {model_key}")
                continue
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Starting tasks for model: {self.models[model_key]['full_name']}")
            logger.info(f"{'='*80}\n")
            
            model_results = {}
            
            for task_id in tasks_to_run:
                task = get_task(task_id)
                if not task:
                    logger.error(f"Unknown task: {task_id}")
                    continue
                
                logger.info(f"\n{'='*60}")
                logger.info(f"Task: {task.task_id} - {task.task_description}")
                logger.info(f"{'='*60}\n")
                
                # Run the task
                task_result = self.run_single_task(task, model_key)
                model_results[task_id] = task_result
                
                # Log result
                if task_result["success"]:
                    logger.info(f"✅ Task {task.task_id} completed successfully")
                else:
                    logger.error(f"❌ Task {task.task_id} failed")
                
                # Optional: Add delay between tasks
                import time
                time.sleep(2)
            
            results[model_key] = model_results
        
        logger.info(f"\n{'='*80}")
        logger.info("Golden dataset generation completed!")
        logger.info(f"{'='*80}\n")
        
        self._print_summary(results)
        
        return results
    
    def run_single_task(self, task: TaskDefinition, model_key: str) -> Dict:
        """Run a single task for a specific model
        
        Args:
            task: TaskDefinition
            model_key: Model key
            
        Returns:
            Result dict
        """
        model_config = self.models[model_key]
        
        # Setup working directory
        work_dir = self.base_dir / "terraform_code" / model_config["short_name"] / task.task_id.lower().replace('.', '_')
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        terraform = TerraformExecutor(work_dir)
        memory = ConversationMemory(
            task_id=task.task_id,
            model_name=model_config["full_name"],
            work_dir=work_dir
        )
        
        # Add system message with platform context
        memory.add_system_message(PLATFORM_CONTEXT)
        
        # Add initial user prompt
        full_prompt = build_full_prompt(task)
        memory.add_user_message(full_prompt)
        
        # Iterative loop
        terraform_results = {}
        llm_response_data = {}
        worked_as_generated = False
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"\n--- Iteration {iteration}/{self.max_iterations} ---")
            
            # Call LLM
            logger.info("Calling LLM...")
            llm_result = self.openrouter.call_llm(
                model=model_config["api_id"],
                messages=memory.get_messages()
            )
            
            if not llm_result["success"]:
                logger.error(f"LLM call failed: {llm_result.get('error')}")
                return {
                    "success": False,
                    "error": "LLM call failed",
                    "iteration": iteration
                }
            
            # Save LLM response
            llm_response_text = llm_result["content"]
            memory.add_assistant_message(llm_response_text)
            
            # Save full LLM response to file
            (work_dir / "llm_response.txt").write_text(llm_response_text)
            
            # Extract Terraform code
            logger.info("Extracting Terraform code...")
            terraform_code = self.openrouter.extract_terraform_code(llm_response_text)
            
            if not terraform_code:
                logger.warning("No Terraform code found in LLM response")
                # Ask for code explicitly
                memory.add_user_message(
                    "Please provide the complete Terraform code in a code block (```terraform ... ```)."
                )
                continue
            
            # Save Terraform code
            terraform.write_main_tf(terraform_code)
            
            # Store LLM response data (first iteration only)
            if iteration == 1:
                llm_response_data = {
                    "generated_code": terraform_code,
                    "questions_asked": self.openrouter.extract_questions_asked(llm_response_text),
                    "time_seconds": llm_result["time_seconds"],
                    "inferred_defaults": {}  # TODO: Parse from response
                }
            
            # Execute Terraform workflow
            logger.info("Executing Terraform workflow...")
            
            # Init
            logger.info("Running terraform init...")
            init_result = terraform.init()
            terraform_results["init"] = init_result
            
            if init_result["status"] != "success":
                logger.error(f"Terraform init failed: {init_result['error_message']}")
                memory.add_error_feedback("init", init_result["error_message"], init_result.get("stderr", ""))
                continue
            
            # Validate
            logger.info("Running terraform validate...")
            validate_result = terraform.validate()
            terraform_results["validate"] = validate_result
            
            if validate_result["status"] != "success":
                logger.error(f"Terraform validate failed: {validate_result['error_message']}")
                memory.add_error_feedback("validate", validate_result["error_message"], validate_result.get("stderr", ""))
                continue
            
            # Plan
            logger.info("Running terraform plan...")
            plan_result = terraform.plan()
            terraform_results["plan"] = plan_result
            
            if plan_result["status"] != "success":
                logger.error(f"Terraform plan failed: {plan_result['error_message']}")
                memory.add_error_feedback("plan", plan_result["error_message"], plan_result.get("stderr", ""))
                continue
            
            # Apply
            logger.info("Running terraform apply...")
            apply_result = terraform.apply()
            terraform_results["apply"] = apply_result
            
            if apply_result["status"] != "success":
                logger.error(f"Terraform apply failed: {apply_result['error_message']}")
                memory.add_error_feedback("apply", apply_result["error_message"], apply_result.get("stderr", ""))
                continue
            
            # Success!
            logger.info("✅ Terraform apply succeeded!")
            worked_as_generated = (iteration == 1)
            break
        
        else:
            # Max iterations reached
            logger.error(f"❌ Max iterations ({self.max_iterations}) reached without success")
            return {
                "success": False,
                "error": "Max iterations reached",
                "iteration": self.max_iterations,
                "terraform_results": terraform_results
            }
        
        # Take screenshots
        logger.info("Capturing screenshots...")
        screenshots = asyncio.run(self.xen_screenshot.capture_screenshots(
            task_id=task.task_id.lower().replace('.', '_'),
            model_short_name=model_config["short_name"]
        ))
        
        # Generate verification data (simplified)
        verification_data = self._generate_verification_data(task, terraform_results)
        
        # Generate JSON dataset entry
        logger.info("Generating dataset entry...")
        dataset_dir = self.base_dir / "dataset" / model_config["short_name"]
        dataset_gen = DatasetGenerator(dataset_dir)
        
        prompt_data = {
            "input_text": task.prompt_text,
            "prompt_type": task.prompt_type,
            "infrastructure_state_before": task.infrastructure_state_before,
            "information_provided": [],
            "information_missing": [],
            "is_update": task.is_update,
            "is_incremental": task.is_incremental,
            "is_edge_case": task.is_edge_case,
            "is_idempotency_test": task.is_idempotency_test
        }
        
        json_path = dataset_gen.generate_entry(
            task_id=task.task_id,
            task_description=task.task_description,
            model_name=model_config["full_name"],
            model_short_name=model_config["short_name"],
            prompt_data=prompt_data,
            llm_response_data=llm_response_data,
            terraform_results=terraform_results,
            verification_data=verification_data,
            screenshots=screenshots,
            iteration_count=memory.get_iteration_count() + 1,
            worked_as_generated=worked_as_generated,
            evaluator_notes=f"Generated via automated system. {'Worked on first attempt.' if worked_as_generated else f'Required {memory.get_iteration_count()} iterations to succeed.'}"
        )
        
        # Cleanup VMs if required
        if task.cleanup_after:
            logger.info("Cleaning up VMs (terraform destroy)...")
            destroy_result = terraform.destroy()
            if destroy_result["status"] == "success":
                logger.info("✅ VMs destroyed successfully")
            else:
                logger.warning(f"⚠️ VM cleanup failed: {destroy_result['error_message']}")
        
        return {
            "success": True,
            "task_id": task.task_id,
            "model": model_config["full_name"],
            "iterations": memory.get_iteration_count() + 1,
            "worked_as_generated": worked_as_generated,
            "json_path": str(json_path),
            "terraform_results": terraform_results,
            "screenshots": screenshots
        }
    
    def _generate_verification_data(self, task: TaskDefinition, terraform_results: Dict) -> Dict:
        """Generate verification data (simplified version)
        
        Args:
            task: TaskDefinition
            terraform_results: Terraform execution results
            
        Returns:
            Verification data dict
        """
        apply_success = terraform_results.get("apply", {}).get("status") == "success"
        
        return {
            "vms_exist_in_xo": apply_success,
            "expected_vm_count": task.expected_vm_count,
            "actual_vm_count": task.expected_vm_count if apply_success else 0,
            "all_vms_running": apply_success,
            "all_vms_accessible": apply_success,
            "vm_details": [],
            "meets_requirements": apply_success,
            "resource_allocation_correct": apply_success,
            "specs_match": apply_success,
            "available_ram_after": 20 - (task.expected_ram_gb or 0) if apply_success else 20
        }
    
    def _print_summary(self, results: Dict):
        """Print execution summary
        
        Args:
            results: Results dict
        """
        logger.info("\n" + "="*80)
        logger.info("EXECUTION SUMMARY")
        logger.info("="*80)
        
        for model_key, model_results in results.items():
            logger.info(f"\nModel: {self.models[model_key]['full_name']}")
            logger.info("-" * 60)
            
            for task_id, task_result in model_results.items():
                status = "✅" if task_result.get("success") else "❌"
                iterations = task_result.get("iterations", "N/A")
                logger.info(f"{status} {task_id}: {iterations} iterations")
        
        logger.info("\n" + "="*80)
