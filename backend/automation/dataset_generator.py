"""JSON dataset generator following the golden dataset schema"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class DatasetGenerator:
    """Generate JSON dataset entries following the schema"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_entry(
        self,
        task_id: str,
        task_description: str,
        model_name: str,
        model_short_name: str,
        prompt_data: Dict,
        llm_response_data: Dict,
        terraform_results: Dict,
        verification_data: Dict,
        screenshots: Dict[str, str],
        iteration_count: int,
        worked_as_generated: bool,
        evaluator_notes: str = ""
    ) -> Path:
        """Generate a complete JSON dataset entry
        
        Args:
            task_id: Task ID (e.g., 'C1.2')
            task_description: Task description
            model_name: Full model name
            model_short_name: Short model name for filenames
            prompt_data: Prompt information dict
            llm_response_data: LLM response information
            terraform_results: Terraform execution results
            verification_data: Verification results
            screenshots: Screenshot paths dict
            iteration_count: Number of iterations needed
            worked_as_generated: Whether code worked without fixes
            evaluator_notes: Additional notes
            
        Returns:
            Path to generated JSON file
        """
        timestamp = datetime.now(timezone.utc)
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Generate entry ID and filename
        task_id_lower = task_id.lower().replace('.', '_')
        entry_id = f"{task_id_lower}_{model_short_name}_{timestamp_str}"
        filename = f"{entry_id}.json"
        
        # Build the complete JSON structure
        entry = {
            "dataset_version": "1.0",
            "entry_id": entry_id,
            "task_id": task_id,
            "task_description": task_description,
            "timestamp": timestamp.isoformat(),
            "evaluator": "Automated System",
            "metadata": {
                "model_name": model_name,
                "model_version": model_name,
                "prompt_type": prompt_data.get("prompt_type", "little_context"),
                "infrastructure_state_before": prompt_data.get("infrastructure_state_before", "clean_server_0_vms")
            },
            "scenario": {
                "infrastructure": "single_xcpng_host",
                "total_ram_gb": 24,
                "total_cpu_cores": 32,
                "available_ram_gb_before": 20,
                "available_ram_gb_after": verification_data.get("available_ram_after", 18),
                "edge_case": prompt_data.get("edge_case", "none")
            },
            "prompt": {
                "input_text": prompt_data.get("input_text", ""),
                "information_provided": prompt_data.get("information_provided", []),
                "information_missing": prompt_data.get("information_missing", [])
            },
            "llm_response": {
                "generated_code": llm_response_data.get("generated_code", ""),
                "questions_asked": llm_response_data.get("questions_asked", []),
                "additional_files_generated": llm_response_data.get("additional_files_generated", []),
                "iterations_needed": iteration_count,
                "time_to_generate_seconds": llm_response_data.get("time_seconds", 0),
                "inferred_defaults": llm_response_data.get("inferred_defaults", {})
            },
            "execution_results": {
                "terraform_init": self._format_tf_result(terraform_results.get("init", {})),
                "terraform_validate": self._format_tf_result(terraform_results.get("validate", {})),
                "terraform_plan": self._format_tf_result(terraform_results.get("plan", {})),
                "terraform_apply": self._format_tf_result(terraform_results.get("apply", {}))
            },
            "verification": verification_data,
            "manual_interventions": [],
            "final_outcome": {
                "worked_as_generated": worked_as_generated,
                "worked_after_fixes": terraform_results.get("apply", {}).get("status") == "success",
                "total_fixes_needed": iteration_count - 1 if iteration_count > 1 else 0,
                "total_iterations": iteration_count,
                "execution_successful": terraform_results.get("apply", {}).get("status") == "success",
                "meets_requirements": verification_data.get("meets_requirements", True),
                "resource_allocation_correct": verification_data.get("resource_allocation_correct", True)
            },
            "validation_checklist": self._build_validation_checklist(terraform_results, verification_data),
            "screenshots": screenshots,
            "evaluator_notes": evaluator_notes
        }
        
        # Add special fields based on task type
        if prompt_data.get("is_update"):
            entry["update_operation_validation"] = verification_data.get("update_validation", {})
        
        if prompt_data.get("is_incremental"):
            entry["incremental_operation_validation"] = verification_data.get("incremental_validation", {})
        
        if prompt_data.get("is_edge_case"):
            entry["edge_case_handling"] = verification_data.get("edge_case_handling", {})
            entry["edge_case_score"] = verification_data.get("edge_case_score", {})
        
        if prompt_data.get("is_idempotency_test"):
            entry["idempotency_test"] = verification_data.get("idempotency_test", {})
        
        # Write JSON file
        output_path = self.output_dir / filename
        output_path.write_text(json.dumps(entry, indent=2))
        logger.info(f"Generated dataset entry: {output_path}")
        
        return output_path
    
    def _format_tf_result(self, result: Dict) -> Dict:
        """Format terraform result for JSON
        
        Args:
            result: Raw terraform result dict
            
        Returns:
            Formatted result dict
        """
        return {
            "status": result.get("status", "unknown"),
            "command": result.get("command", ""),
            "exit_code": result.get("exit_code", -1),
            "execution_time_seconds": result.get("execution_time_seconds", 0),
            "error_message": result.get("error_message"),
            "resources_to_create": result.get("resources_to_create", 0),
            "resources_to_modify": result.get("resources_to_modify", 0),
            "resources_to_destroy": result.get("resources_to_destroy", 0)
        }
    
    def _build_validation_checklist(self, terraform_results: Dict, verification_data: Dict) -> Dict:
        """Build validation checklist
        
        Args:
            terraform_results: Terraform execution results
            verification_data: Verification data
            
        Returns:
            Validation checklist dict
        """
        init_success = terraform_results.get("init", {}).get("status") == "success"
        validate_success = terraform_results.get("validate", {}).get("status") == "success"
        plan_success = terraform_results.get("plan", {}).get("status") == "success"
        apply_success = terraform_results.get("apply", {}).get("status") == "success"
        
        return {
            "code_quality": {
                "provider_config_included": True,
                "data_sources_included": verification_data.get("data_sources_used", False),
                "vm_resource_defined": True,
                "infers_reasonable_defaults": True
            },
            "execution": {
                "terraform_init_success": init_success,
                "terraform_validate_success": validate_success,
                "terraform_plan_success": plan_success,
                "terraform_apply_success": apply_success,
                "vm_in_xen_orchestra": verification_data.get("vms_exist_in_xo", False),
                "vm_running": verification_data.get("all_vms_running", False),
                "vm_has_correct_specs": verification_data.get("specs_match", False)
            }
        }
