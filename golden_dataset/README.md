# Golden Dataset Automation System

Automated system for testing LLMs (DeepSeek R1 and Google Gemini 3 Pro) on Terraform VM provisioning tasks.

## Overview

This system automates the entire workflow of:
1. Calling LLMs to generate Terraform code
2. Executing Terraform (init, validate, plan, apply)
3. Handling errors with iterative feedback loops
4. Capturing screenshots from Xen Orchestra
5. Generating structured JSON datasets
6. Managing VM cleanup

## Features

- ✅ **13 Predefined Tasks**: CREATE, READ, UPDATE, DELETE operations
- ✅ **Multi-Model Support**: DeepSeek R1 & Google Gemini 3 Pro
- ✅ **Iterative Error Handling**: Up to 20 retry attempts with memory
- ✅ **Task-Specific Memory**: Isolated conversation history per task
- ✅ **Comprehensive Logging**: All Terraform logs saved
- ✅ **Screenshot Automation**: Xen Orchestra web UI capture
- ✅ **JSON Dataset Generation**: Follows golden dataset schema
- ✅ **Dependency Management**: Smart task ordering
- ✅ **VM Cleanup**: Automatic cleanup after tasks

## Prerequisites

1. **OpenRouter API Key**: Required for LLM access
2. **Xen Orchestra**: Running at `localhost:8080`
3. **Terraform**: Installed and in PATH
4. **Playwright**: For screenshot automation

## Installation

```bash
# Install Python dependencies
cd /app/backend
pip install -r requirements.txt

# Install Playwright
pip install playwright
playwright install chromium

# Install Terraform (if not already installed)
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

## Configuration

Create `/app/backend/.env` file:

```bash
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

### Run All Tasks for All Models

```bash
cd /app/backend
python run_automation.py --all
```

### Run Specific Tasks

```bash
python run_automation.py --tasks c1_2 c1_3 c2_2
```

### Run for Specific Model

```bash
python run_automation.py --models deepseek_r1 --all
python run_automation.py --models google_gemini_3_pro --tasks c1_2
```

### Custom Iteration Limit

```bash
python run_automation.py --all --max-iterations 10
```

### Help

```bash
python run_automation.py --help
```

## Task List

| Task ID | Description | Type | VMs | Cleanup |
|---------|-------------|------|-----|----------|
| c1_2 | Single VM with 2GB RAM - Little Context | CREATE | 1 | Yes |
| c1_3 | Single VM - Detailed Prompt | CREATE | 1 | No* |
| c2_2 | Multiple Identical VMs - Little Context | CREATE | 3 | Yes |
| c2_3 | Multiple Identical VMs - Detailed | CREATE | 3 | No* |
| r1_2 | List Existing VMs | READ | 3 | No |
| u1_2 | Increase RAM | UPDATE | 1 | No* |
| d1_2 | Delete Single VM | DELETE | 0 | Yes |
| d2_2 | Delete Multiple VMs | DELETE | 1 | Yes |
| c4_2 | Incremental VM Addition | CREATE | 4 | Yes |
| c5_2 | Over-Provisioning Edge Case | CREATE | 0 | Yes |

*Kept for dependent tasks

## Directory Structure

```
/app/golden_dataset/
├── dataset/
│   ├── deepseek_r1/
│   │   ├── c1_2_deepseek_r1_20250128_143022.json
│   │   └── ... (all 13 tasks)
│   └── google_gemini_3_pro/
│       ├── c1_2_google_gemini_3_pro_20250128_143500.json
│       └── ... (all 13 tasks)
├── screenshots/
│   ├── c1_2_deepseek_r1_xo_list.png
│   ├── c1_2_deepseek_r1_vm_details.png
│   └── ... (all screenshots)
├── terraform_code/
│   ├── deepseek_r1/
│   │   ├── c1_2/
│   │   │   ├── main.tf
│   │   │   ├── init.log
│   │   │   ├── validate.log
│   │   │   ├── plan.log
│   │   │   ├── apply.log
│   │   │   └── llm_response.txt
│   │   └── ... (all tasks)
│   └── google_gemini_3_pro/
│       └── ... (all tasks)
└── logs/
    └── automation.log
```

## Output

Each task execution generates:

1. **JSON Dataset Entry**: Complete evaluation data following schema
2. **Terraform Code**: `main.tf` file
3. **Execution Logs**: init, validate, plan, apply, destroy logs
4. **LLM Response**: Full response text
5. **Conversation History**: All messages exchanged
6. **Screenshots**: VM list, details, resource usage

## Models

### DeepSeek R1
- **API ID**: `deepseek/deepseek-r1`
- **Short Name**: `deepseek_r1`

### Google Gemini 3 Pro
- **API ID**: `google/gemini-pro-1.5`
- **Short Name**: `google_gemini_3_pro`

## Iteration Logic

1. **Initial Prompt**: Send task prompt to LLM
2. **Extract Code**: Parse Terraform code from response
3. **Execute Terraform**: Run init → validate → plan → apply
4. **On Error**: Send error feedback to LLM with logs
5. **Retry**: LLM generates fixed code
6. **Repeat**: Until success or max iterations
7. **On Success**: Capture screenshots, generate dataset
8. **Cleanup**: Destroy VMs if required

## Memory Management

Each task maintains isolated conversation history:
- System message with platform context
- User messages (prompts, feedback)
- Assistant messages (LLM responses)
- Iteration counter
- Saved to `conversation_history.json`

## Logging

All logs saved to:
- `/app/golden_dataset/logs/automation.log` - Main automation log
- Individual Terraform logs per task
- Console output with progress indicators

## Troubleshooting

### API Key Not Found
```bash
export OPENROUTER_API_KEY="your_key_here"
# Or add to /app/backend/.env
```

### Terraform Not Found
```bash
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### Playwright Not Installed
```bash
pip install playwright
playwright install chromium
```

### Xen Orchestra Not Accessible
- Check if XO is running: `curl http://localhost:8080`
- Verify credentials: `admin@admin.net` / `admin`
- Check network connectivity

## Advanced Usage

### Custom Model Configuration

Edit `automation/orchestrator.py` to add new models:

```python
self.models["custom_model"] = {
    "full_name": "Custom Model Name",
    "api_id": "provider/model-id",
    "short_name": "custom_model"
}
```

### Add New Tasks

Edit `automation/task_definitions.py`:

```python
TASKS["custom_task"] = TaskDefinition(
    task_id="CUSTOM.1",
    task_description="Your custom task",
    prompt_text="Your prompt here",
    # ... other fields
)
```

## License

MIT License
