#!/usr/bin/env python3
"""
Generate a visual workflow diagram for the automation system
"""

def print_workflow_diagram():
    diagram = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    GOLDEN DATASET AUTOMATION WORKFLOW                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝

                                [USER RUNS]
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │  run_automation.py     │
                         │  --all                 │
                         │  --tasks c1_2 c1_3     │
                         │  --models deepseek_r1  │
                         └───────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │    ORCHESTRATOR        │
                         │  • Load models config  │
                         │  • Load task defs      │
                         │  • Setup directories   │
                         └───────────┬────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     │                               │
                     ▼                               ▼
          ┌───────────────────┐         ┌───────────────────┐
          │  DeepSeek R1      │         │ Google Gemini 3 Pro│
          │  Model Loop       │         │  Model Loop        │
          └─────────┬─────────┘         └─────────┬──────────┘
                    │                               │
                    │         [For each task]       │
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     SINGLE TASK EXECUTION     │
                    │  • Create work directory      │
                    │  • Initialize memory          │
                    │  • Add platform context       │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          ITERATION LOOP (Max 20)                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ STEP 1: CALL LLM                                                        │  ║
║  │  • OpenRouter API with model                                           │  ║
║  │  • Send conversation messages                                          │  ║
║  │  • Include platform context                                            │  ║
║  │  • Get Terraform code response                                         │  ║
║  └────────────────────┬───────────────────────────────────────────────────┘  ║
║                       │                                                       ║
║                       ▼                                                       ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ STEP 2: EXTRACT CODE                                                    │  ║
║  │  • Parse Terraform code blocks                                         │  ║
║  │  • Extract questions asked by LLM                                      │  ║
║  │  • Save full LLM response to file                                     │  ║
║  │  • Write main.tf                                                       │  ║
║  └────────────────────┬───────────────────────────────────────────────────┘  ║
║                       │                                                       ║
║                       ▼                                                       ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ STEP 3: TERRAFORM INIT                                                  │  ║
║  │  • terraform init                                                      │  ║
║  │  • Capture logs to init.log                                           │  ║
║  │  • Check exit code                                                    │  ║
║  └────────────────────┬───────────────────────────────────────────────────┘  ║
║                       │                                                       ║
║                       ├──[FAIL]──> Add error feedback ──┐                     ║
║                       │                                 │                     ║
║                       ▼                                 │                     ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ STEP 4: TERRAFORM VALIDATE                                              │  ║
║  │  • terraform validate                                                  │  ║
║  │  • Capture logs to validate.log                                       │  ║
║  │  • Check exit code                                                    │  ║
║  └────────────────────┬───────────────────────────────────────────────────┘  ║
║                       │                                 │                     ║
║                       ├──[FAIL]──> Add error feedback ──┤                     ║
║                       │                                 │                     ║
║                       ▼                                 │                     ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ STEP 5: TERRAFORM PLAN                                                  │  ║
║  │  • terraform plan -out=tfplan                                          │  ║
║  │  • Capture logs to plan.log                                           │  ║
║  │  • Parse resource counts                                              │  ║
║  │  • Generate plan_readable.txt                                         │  ║
║  └────────────────────┬───────────────────────────────────────────────────┘  ║
║                       │                                 │                     ║
║                       ├──[FAIL]──> Add error feedback ──┤                     ║
║                       │                                 │                     ║
║                       ▼                                 │                     ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │ STEP 6: TERRAFORM APPLY                                                 │  ║
║  │  • terraform apply -auto-approve                                       │  ║
║  │  • Capture logs to apply.log                                          │  ║
║  │  • Check exit code                                                    │  ║
║  └────────────────────┬───────────────────────────────────────────────────┘  ║
║                       │                                 │                     ║
║                       ├──[FAIL]──> Add error feedback ──┤                     ║
║                       │                                 │                     ║
║                       ▼                                 │                     ║
║                  [SUCCESS!]                             │                     ║
║                       │                                 │                     ║
║                       │                                 ▼                     ║
║                       │                    ┌──────────────────────────────┐   ║
║                       │                    │  MEMORY UPDATE               │   ║
║                       │                    │  • Add error message         │   ║
║                       │                    │  • Add logs excerpt          │   ║
║                       │                    │  • Increment iteration       │   ║
║                       │                    │  • Save conversation         │   ║
║                       │                    └──────────────┬───────────────┘   ║
║                       │                                   │                   ║
║                       │                    Iteration < 20?│                   ║
║                       │                                   │                   ║
║                       │                    ┌──────────[YES]                   ║
║                       │                    │              │                   ║
║                       │                    └──────────────┘                   ║
║                       │                    Loop to STEP 1                     ║
║                       │                                                       ║
║                       │                    [NO] → MAX ITERATIONS REACHED      ║
║                       │                          TASK FAILED                  ║
║                       │                                                       ║
╚═══════════════════════┼═══════════════════════════════════════════════════════╝
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │  POST-SUCCESS ACTIONS                 │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ SCREENSHOTS│  │   VERIFY   │  │  DATASET   │
│            │  │            │  │ GENERATION │
│ • Login XO │  │ • Check VMs│  │            │
│ • VM list  │  │ • Get specs│  │ • Build    │
│ • Details  │  │ • Validate │  │   JSON     │
│ • Resources│  │   counts   │  │ • Save to  │
│            │  │            │  │   file     │
└────────┬───┘  └────────┬───┘  └────────┬───┘
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  CLEANUP (if required)        │
         │  • terraform destroy          │
         │  • Capture destroy.log        │
         │  • Verify VMs removed         │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   TASK COMPLETE               │
         │   • JSON file saved           │
         │   • Screenshots saved         │
         │   • Logs saved                │
         │   • Move to next task         │
         └───────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

FINAL OUTPUT STRUCTURE:

/app/golden_dataset/
├── dataset/
│   └── {model}/
│       └── {task}_{model}_{timestamp}.json
├── screenshots/
│   └── {task}_{model}_{type}.png
├── terraform_code/
│   └── {model}/
│       └── {task}/
│           ├── main.tf
│           ├── init.log
│           ├── validate.log
│           ├── plan.log
│           ├── apply.log
│           ├── llm_response.txt
│           └── conversation_history.json
└── logs/
    └── automation.log

═══════════════════════════════════════════════════════════════════════════════

KEY FEATURES:
✅ Task-specific memory (no cross-contamination)
✅ Up to 20 retry iterations with full error feedback
✅ Comprehensive logging at every step
✅ Screenshot automation with Playwright
✅ JSON dataset following exact schema
✅ Smart VM cleanup based on dependencies
✅ Progress monitoring and reporting

═══════════════════════════════════════════════════════════════════════════════
"""
    print(diagram)

if __name__ == "__main__":
    print_workflow_diagram()
