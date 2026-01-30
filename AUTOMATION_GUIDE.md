# Golden Dataset Automation System - Complete Guide

## 🎯 Overview

This is a comprehensive automation system for testing Large Language Models (LLMs) on Terraform VM provisioning tasks using Xen Orchestra. It automatically:

1. Calls LLMs (DeepSeek R1 & Google Gemini 3 Pro) to generate Terraform code
2. Executes Terraform commands with comprehensive logging
3. Handles errors through iterative feedback loops with memory
4. Captures screenshots from Xen Orchestra web interface
5. Generates structured JSON datasets following a specific schema
6. Manages VM lifecycle with smart cleanup

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   CLI Runner (run_automation.py)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator (orchestrator.py)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - Task Management                                   │   │
│  │  - Model Configuration                               │   │
│  │  - Workflow Coordination                             │   │
│  └─────────────────────────────────────────────────────┘   │
└───┬─────────────┬─────────────┬──────────────┬─────────────┘
    │             │             │              │
    ▼             ▼             ▼              ▼
┌─────────┐  ┌─────────┐  ┌──────────┐  ┌────────────┐
│OpenRouter│  │Terraform│  │   Xen    │  │  Dataset   │
│ Client  │  │Executor │  │Screenshot│  │ Generator  │
└─────────┘  └─────────┘  └──────────┘  └────────────┘
     │            │             │              │
     ▼            ▼             ▼              ▼
┌─────────┐  ┌─────────┐  ┌──────────┐  ┌────────────┐
│  LLM    │  │Terraform│  │   Xen    │  │    JSON    │
│  API    │  │  Logs   │  │Orchestra │  │   Files    │
└─────────┘  └─────────┘  └──────────┘  └────────────┘
```

## 🔧 Components

### 1. OpenRouter Client (`openrouter_client.py`)
- Communicates with OpenRouter API
- Handles LLM calls with proper error handling
- Extracts Terraform code from responses
- Parses questions asked by LLM

### 2. Terraform Executor (`terraform_executor.py`)
- Wraps Terraform CLI commands
- Captures detailed logs for all operations
- Parses plan output for resource counts
- Handles timeouts and errors gracefully

### 3. Xen Screenshot (`xen_screenshot.py`)
- Automates Playwright browser
- Logs into Xen Orchestra
- Captures VM list, details, and resource screenshots
- Handles errors with placeholder generation

### 4. Memory Manager (`memory_manager.py`)
- Maintains conversation history per task
- Isolates memory between tasks
- Tracks iteration counts
- Saves/loads conversation state

### 5. Dataset Generator (`dataset_generator.py`)
- Creates JSON files following schema
- Formats execution results
- Builds validation checklists
- Handles special task types (update, incremental, edge cases)

### 6. Task Definitions (`task_definitions.py`)
- Defines all 13 tasks
- Manages dependencies
- Provides platform context
- Controls cleanup behavior

### 7. Orchestrator (`orchestrator.py`)
- Main workflow coordinator
- Manages task execution
- Handles iterative loops
- Coordinates all components

## 📝 Task Definitions

### CREATE Operations

#### C1.2 - Single VM (Little Context)
- **Prompt**: "Create an Ubuntu VM with 2GB RAM"
- **Expected**: 1 VM with 2GB RAM, reasonable defaults
- **Cleanup**: Yes

#### C1.3 - Single VM (Detailed)
- **Prompt**: "Create an Ubuntu 22.04 VM named 'app-01' with 2 vCPU, 4GB RAM, 50GB disk on 'local-storage', connected to 'xenbr0' with DHCP"
- **Expected**: Exact specifications met
- **Cleanup**: No (kept for U1.2)

#### C2.2 - Multiple VMs (Little Context)
- **Prompt**: "Create 3 Ubuntu VMs, each with 2GB RAM"
- **Expected**: 3 identical VMs with sequential naming
- **Cleanup**: Yes

#### C2.3 - Multiple VMs (Detailed + Idempotency)
- **Prompt**: "Create 3 Ubuntu 22.04 VMs named 'web-01', 'web-02', 'web-03', each with 2 vCPU, 4GB RAM, and 50GB disk"
- **Expected**: 3 VMs, idempotent (second plan shows no changes)
- **Cleanup**: No (kept for R1.2)

#### C4.2 - Incremental Addition
- **Prompt**: "Add a new Ubuntu VM named 'web-04' with 2 vCPU and 4GB RAM (keep existing VMs unchanged)"
- **Expected**: New VM added, existing VMs untouched
- **Cleanup**: Yes

#### C5.2 - Edge Case (Over-Provisioning)
- **Prompt**: "Attempt to create 10 Ubuntu VMs, each with 3GB RAM"
- **Expected**: LLM should recognize over-provisioning, warn, suggest alternatives
- **Cleanup**: Yes

### READ Operations

#### R1.2 - List VMs
- **Prompt**: "List all existing VMs and their RAM allocation"
- **Expected**: Data source usage, correct output
- **Depends On**: C2.3
- **Cleanup**: No

### UPDATE Operations

#### U1.2 - Increase RAM
- **Prompt**: "Increase the RAM of the 'app-01' VM to 6GB"
- **Expected**: In-place update, no VM recreation, UUID unchanged
- **Depends On**: C1.3
- **Cleanup**: No (kept for D1.2)

### DELETE Operations

#### D1.2 - Delete Single VM
- **Prompt**: "Remove the 'app-01' VM from the infrastructure"
- **Expected**: VM deleted, Terraform plan shows -1
- **Depends On**: U1.2
- **Cleanup**: Yes

#### D2.2 - Delete Multiple VMs
- **Prompt**: "Remove 'web-02' and 'web-03' VMs from the infrastructure"
- **Expected**: 2 VMs deleted, web-01 remains
- **Depends On**: R1.2
- **Cleanup**: Yes

## 🔄 Iteration Logic

```
┌─────────────────────┐
│  Initialize Task    │
│  - Setup work dir   │
│  - Create memory    │
│  - Add platform ctx │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Send Prompt to LLM │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Extract Terraform   │
│ Code from Response  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  terraform init     │
└──────────┬──────────┘
           │
           ├─Success──────┐
           │              │
           │              ▼
           │      ┌──────────────┐
           │      │  terraform   │
           │      │  validate    │
           │      └──────┬───────┘
           │             │
           │             ├─Success──┐
           │             │          │
           │             │          ▼
           │             │   ┌──────────┐
           │             │   │terraform │
           │             │   │  plan    │
           │             │   └────┬─────┘
           │             │        │
           │             │        ├─Success─┐
           │             │        │         │
           │             │        │         ▼
           │             │        │  ┌──────────┐
           │             │        │  │terraform │
           │             │        │  │  apply   │
           │             │        │  └────┬─────┘
           │             │        │       │
           │             │        │       ├─Success─┐
           │             │        │       │         │
           │             │        │       │         ▼
           │             │        │       │   ┌──────────┐
           │             │        │       │   │ SUCCESS! │
           │             │        │       │   │ Take     │
           │             │        │       │   │ Screenshots│
           │             │        │       │   │ Generate │
           │             │        │       │   │ Dataset  │
           │             │        │       │   └──────────┘
           │             │        │       │
           ▼             ▼        ▼       ▼
        ┌─────────────────────────────────┐
        │  Add Error Feedback to Memory   │
        │  - Include error message        │
        │  - Include relevant logs        │
        │  - Increment iteration counter  │
        └─────────────┬───────────────────┘
                      │
                      │ Iteration < Max?
                      │
                      ├─Yes─────┐
                      │         │
                      │         ▼
                      │    ┌─────────────┐
                      │    │  Call LLM   │
                      │    │  with error │
                      │    │  feedback   │
                      │    └──────┬──────┘
                      │           │
                      │           └───────────┐
                      │                       │
                      ▼                       │
                 ┌─────────┐                 │
                 │  FAILED │◄────────────────┘
                 └─────────┘
```

## 🗂️ Directory Structure

```
/app/
├── backend/
│   ├── automation/
│   │   ├── __init__.py
│   │   ├── openrouter_client.py      # LLM API client
│   │   ├── terraform_executor.py     # Terraform wrapper
│   │   ├── xen_screenshot.py         # Screenshot automation
│   │   ├── memory_manager.py         # Conversation history
│   │   ├── dataset_generator.py      # JSON generator
│   │   ├── task_definitions.py       # Task configurations
│   │   └── orchestrator.py           # Main coordinator
│   ├── run_automation.py             # CLI entry point
│   ├── test_setup.py                 # Setup validator
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Configuration
│
└── golden_dataset/
    ├── dataset/
    │   ├── deepseek_r1/
    │   │   ├── c1_2_deepseek_r1_20250128_143022.json
    │   │   ├── c1_3_deepseek_r1_20250128_144501.json
    │   │   └── ... (all 13 tasks)
    │   └── google_gemini_3_pro/
    │       ├── c1_2_google_gemini_3_pro_20250128_143500.json
    │       └── ... (all 13 tasks)
    │
    ├── screenshots/
    │   ├── c1_2_deepseek_r1_xo_list.png
    │   ├── c1_2_deepseek_r1_vm_details.png
    │   ├── c1_2_deepseek_r1_resources.png
    │   └── ... (all screenshots)
    │
    ├── terraform_code/
    │   ├── deepseek_r1/
    │   │   ├── c1_2/
    │   │   │   ├── main.tf
    │   │   │   ├── init.log
    │   │   │   ├── validate.log
    │   │   │   ├── plan.log
    │   │   │   ├── plan_readable.txt
    │   │   │   ├── apply.log
    │   │   │   ├── llm_response.txt
    │   │   │   └── conversation_history.json
    │   │   └── ... (all 13 tasks)
    │   └── google_gemini_3_pro/
    │       └── ... (all 13 tasks)
    │
    ├── logs/
    │   └── automation.log
    │
    └── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /app/backend

# Install Python packages
pip install -r requirements.txt

# Install Playwright and browsers
pip install playwright
playwright install chromium

# Install Terraform (if needed)
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### 2. Configure API Key

Edit `/app/backend/.env`:

```bash
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 3. Validate Setup

```bash
python test_setup.py
```

### 4. Run Automation

```bash
# Run all tasks for all models
python run_automation.py --all

# Run specific tasks
python run_automation.py --tasks c1_2 c1_3

# Run for specific model
python run_automation.py --models deepseek_r1 --all

# Custom iteration limit
python run_automation.py --all --max-iterations 10
```

## 📊 Output Files

### JSON Dataset Entry

Each task generates a comprehensive JSON file with:

- **metadata**: Model info, prompt type, infrastructure state
- **scenario**: Server resources, edge cases
- **prompt**: Input text, provided/missing info
- **llm_response**: Generated code, questions, defaults
- **execution_results**: All Terraform command results
- **verification**: VM details, validation checks
- **final_outcome**: Success metrics, iteration counts
- **validation_checklist**: Code quality, execution checks
- **screenshots**: Paths to all captured images
- **evaluator_notes**: Additional observations

### Terraform Logs

- `init.log`: Terraform initialization output
- `validate.log`: Validation results
- `plan.log`: Planning output with resource changes
- `plan_readable.txt`: Human-readable plan
- `apply.log`: Apply execution log
- `destroy.log`: Cleanup log (if applicable)

### LLM Data

- `llm_response.txt`: Complete LLM response
- `conversation_history.json`: Full conversation with memory

### Screenshots

- `{task}_xo_list.png`: VM list view
- `{task}_vm_details.png`: Individual VM details
- `{task}_resources.png`: Resource usage view

## 🔍 Monitoring & Debugging

### Check Logs

```bash
# Main automation log
tail -f /app/golden_dataset/logs/automation.log

# Specific task logs
ls /app/golden_dataset/terraform_code/deepseek_r1/c1_2/

# View conversation history
cat /app/golden_dataset/terraform_code/deepseek_r1/c1_2/conversation_history.json | python -m json.tool
```

### Common Issues

#### API Key Not Working
- Verify key in .env file
- Check OpenRouter account has credits
- Test manually: `curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY"`

#### Terraform Errors
- Check Terraform version: `terraform --version`
- Verify provider configuration in main.tf
- Review init.log for provider installation issues

#### Screenshot Failures
- Verify Xen Orchestra is accessible: `curl http://localhost:8080`
- Check Playwright installation: `playwright --version`
- Review browser logs

#### Memory Issues
- Each task has isolated memory
- Check conversation_history.json for debug
- Memory cleared between tasks

## 📈 Performance Optimization

### Parallel Execution (Future Enhancement)
Currently runs sequentially. For parallel:
- Run different models simultaneously
- Use multiprocessing or concurrent.futures
- Be mindful of XO resource limits

### Iteration Limit Tuning
- Default: 20 iterations
- Adjust based on model performance
- Lower for faster testing
- Higher for complex edge cases

### Screenshot Optimization
- Screenshots are optional for testing
- Can disable for faster runs
- Useful for validation and debugging

## 🔐 Security Considerations

- API keys stored in .env (gitignored)
- Xen Orchestra credentials in .env
- Terraform state files contain sensitive data
- Screenshots may contain infrastructure details

## 🧪 Testing

### Validate Setup
```bash
python test_setup.py
```

### Test Single Task
```bash
python run_automation.py --tasks c1_2 --models deepseek_r1
```

### Dry Run (Future)
Add `--dry-run` flag to validate without execution

## 📚 References

- [OpenRouter API Docs](https://openrouter.ai/docs)
- [Terraform Provider: terra-farm/xenorchestra](https://registry.terraform.io/providers/terra-farm/xenorchestra/latest/docs)
- [Playwright Python Docs](https://playwright.dev/python/)
- [Xen Orchestra Docs](https://xen-orchestra.com/docs/)

## 🤝 Contributing

To add new tasks:
1. Edit `task_definitions.py`
2. Add TaskDefinition with proper dependencies
3. Update TASK_ORDER if needed

To add new models:
1. Edit `orchestrator.py`
2. Add model config to `self.models`
3. Ensure OpenRouter supports the model

## 📄 License

MIT License

---

**Built for golden dataset generation and LLM evaluation on Terraform IaC tasks.**
