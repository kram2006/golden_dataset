"""Task definitions for all 13 VM provisioning tasks"""
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TaskDefinition:
    """Definition of a single task"""
    task_id: str
    task_description: str
    prompt_text: str
    prompt_type: str  # vague, little_context, detailed
    operation_type: str  # create, read, update, delete
    expected_vm_count: int
    cleanup_after: bool  # Whether to destroy VMs after this task
    depends_on: Optional[List[str]] = None  # Task IDs this depends on
    infrastructure_state_before: str = "clean_server_0_vms"
    
    # Expected outcomes
    expected_ram_gb: Optional[int] = None
    expected_cpu: Optional[int] = None
    expected_disk_gb: Optional[int] = None
    
    # Special validation
    is_idempotency_test: bool = False
    is_edge_case: bool = False
    is_incremental: bool = False
    is_update: bool = False

# Platform context that will be prepended to all prompts
PLATFORM_CONTEXT = """You are an expert Terraform infrastructure engineer working with Xen Orchestra / XCP-NG.

Platform Details:
- XO WebSocket: ws://localhost:8080
- XO user: admin@admin.net
- XO password: admin
- Pool: DAO-Agentic-Infra
- Network: Pool-wide network associated with eth0
- Disk SR: Local storage
- Installer template: Other install media
- ISO name: ubuntu-22.04.5-live-server-amd64.iso
- ISO UUID: 286a9f23-133c-4cdf-a247-4de9ef4b17e9
- ISO SR: ISO Library

Terraform Provider:
- Provider: xenorchestra
- Source: terra-farm/xenorchestra
- Version: ~> 0.26.0

Server Resources:
- Total RAM: 24GB
- Total CPU: 32 cores
- Available RAM before task: 20GB (approximately)

Please generate working Terraform code that uses the above platform details. Be specific and production-ready.
"""

# Define all 13 tasks
TASKS: Dict[str, TaskDefinition] = {
    "c1_2": TaskDefinition(
        task_id="C1.2",
        task_description="Single VM with 2GB RAM - Little Context",
        prompt_text="Create an Ubuntu VM with 2GB RAM",
        prompt_type="little_context",
        operation_type="create",
        expected_vm_count=1,
        expected_ram_gb=2,
        cleanup_after=True,
        infrastructure_state_before="clean_server_0_vms"
    ),
    
    "c1_3": TaskDefinition(
        task_id="C1.3",
        task_description="Single VM - Detailed Prompt",
        prompt_text="Create an Ubuntu 22.04 VM named 'app-01' with 2 vCPU, 4GB RAM, 50GB disk on 'local-storage', connected to 'xenbr0' with DHCP.",
        prompt_type="detailed",
        operation_type="create",
        expected_vm_count=1,
        expected_ram_gb=4,
        expected_cpu=2,
        expected_disk_gb=50,
        cleanup_after=False,  # Keep for U1.2
        infrastructure_state_before="clean_server_0_vms"
    ),
    
    "c2_2": TaskDefinition(
        task_id="C2.2",
        task_description="Multiple Identical VMs - Little Context",
        prompt_text="Create 3 Ubuntu VMs, each with 2GB RAM",
        prompt_type="little_context",
        operation_type="create",
        expected_vm_count=3,
        expected_ram_gb=6,  # Total
        cleanup_after=True,
        infrastructure_state_before="clean_server_0_vms"
    ),
    
    "c2_3": TaskDefinition(
        task_id="C2.3",
        task_description="Multiple Identical VMs - Detailed + Idempotency",
        prompt_text="Create 3 Ubuntu 22.04 VMs named 'web-01', 'web-02', 'web-03', each with 2 vCPU, 4GB RAM, and 50GB disk, on 'local-storage', connected to 'xenbr0' with DHCP.",
        prompt_type="detailed",
        operation_type="create",
        expected_vm_count=3,
        expected_ram_gb=12,  # Total
        expected_cpu=2,
        expected_disk_gb=50,
        cleanup_after=False,  # Keep for R1.2 and D2.2
        is_idempotency_test=True,
        infrastructure_state_before="clean_server_0_vms"
    ),
    
    "r1_2": TaskDefinition(
        task_id="R1.2",
        task_description="List Existing VMs - Little Context",
        prompt_text="List all existing VMs and their RAM allocation",
        prompt_type="little_context",
        operation_type="read",
        expected_vm_count=3,
        cleanup_after=False,  # Keep for D2.2
        depends_on=["c2_3"],
        infrastructure_state_before="3_vms_from_c2_3"
    ),
    
    "u1_2": TaskDefinition(
        task_id="U1.2",
        task_description="Increase RAM - Little Context",
        prompt_text="Increase the RAM of the 'app-01' VM to 6GB",
        prompt_type="little_context",
        operation_type="update",
        expected_vm_count=1,
        expected_ram_gb=6,
        cleanup_after=False,  # Keep for D1.2
        depends_on=["c1_3"],
        is_update=True,
        infrastructure_state_before="app_01_exists_4gb"
    ),
    
    "d1_2": TaskDefinition(
        task_id="D1.2",
        task_description="Delete Single VM - Little Context",
        prompt_text="Remove the 'app-01' VM from the infrastructure",
        prompt_type="little_context",
        operation_type="delete",
        expected_vm_count=0,
        cleanup_after=True,
        depends_on=["u1_2"],
        infrastructure_state_before="app_01_exists"
    ),
    
    "d2_2": TaskDefinition(
        task_id="D2.2",
        task_description="Delete Multiple VMs - Little Context",
        prompt_text="Remove 'web-02' and 'web-03' VMs from the infrastructure",
        prompt_type="little_context",
        operation_type="delete",
        expected_vm_count=1,  # web-01 remains
        cleanup_after=True,
        depends_on=["r1_2"],
        infrastructure_state_before="3_vms_exist"
    ),
    
    "c4_2": TaskDefinition(
        task_id="C4.2",
        task_description="Incremental VM Addition - Little Context",
        prompt_text="Add a new Ubuntu VM named 'web-04' with 2 vCPU and 4GB RAM to the existing infrastructure (keep existing VMs unchanged)",
        prompt_type="little_context",
        operation_type="create",
        expected_vm_count=4,
        cleanup_after=True,
        is_incremental=True,
        depends_on=["c2_3"],
        infrastructure_state_before="3_vms_exist"
    ),
    
    "c5_2": TaskDefinition(
        task_id="C5.2",
        task_description="Over-Provisioning Edge Case",
        prompt_text="Attempt to create 10 Ubuntu VMs, each with 3GB RAM",
        prompt_type="little_context",
        operation_type="create",
        expected_vm_count=0,  # Should fail or warn
        is_edge_case=True,
        cleanup_after=True,
        infrastructure_state_before="clean_server_0_vms"
    ),
}

# Task execution order (respecting dependencies)
TASK_ORDER = [
    "c1_2",   # Create single VM, then destroy
    "c1_3",   # Create app-01 (keep for U1.2)
    "u1_2",   # Update app-01 RAM
    "d1_2",   # Delete app-01
    "c2_2",   # Create 3 VMs, then destroy
    "c2_3",   # Create web-01, web-02, web-03 (keep for R1.2)
    "r1_2",   # Read VMs
    "c4_2",   # Incremental addition
    "d2_2",   # Delete web-02, web-03
    "c5_2",   # Edge case
]

def get_task(task_id: str) -> Optional[TaskDefinition]:
    """Get task definition by ID
    
    Args:
        task_id: Task identifier (e.g., 'c1_2')
        
    Returns:
        TaskDefinition or None
    """
    return TASKS.get(task_id.lower())

def get_all_tasks() -> List[TaskDefinition]:
    """Get all tasks in execution order
    
    Returns:
        List of TaskDefinitions
    """
    return [TASKS[task_id] for task_id in TASK_ORDER]

def build_full_prompt(task: TaskDefinition) -> str:
    """Build full prompt with platform context
    
    Args:
        task: TaskDefinition
        
    Returns:
        Full prompt string
    """
    return f"{PLATFORM_CONTEXT}\n\nTask: {task.prompt_text}"
