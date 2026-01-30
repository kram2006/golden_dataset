# 🚀 Golden Dataset Automation - Quick Start Guide

## ✅ What Has Been Built

A complete automation system for testing LLMs (DeepSeek R1 & Google Gemini 3 Pro) on Terraform VM provisioning tasks. The system:

✅ **13 Predefined Tasks** - CREATE, READ, UPDATE, DELETE operations
✅ **Iterative Error Handling** - Up to 20 retry attempts with memory
✅ **Task-Specific Memory** - Isolated conversation history per task
✅ **Comprehensive Logging** - All Terraform logs captured
✅ **Screenshot Automation** - Xen Orchestra web UI capture
✅ **JSON Dataset Generation** - Follows golden dataset schema exactly
✅ **Smart Dependencies** - Automatic task ordering and VM cleanup
✅ **Production Ready** - Error handling, timeouts, validation

## 📁 File Structure

```
/app/
├── backend/
│   ├── automation/              # Core automation modules
│   │   ├── openrouter_client.py    # LLM API integration
│   │   ├── terraform_executor.py   # Terraform wrapper
│   │   ├── xen_screenshot.py       # Screenshot automation
│   │   ├── memory_manager.py       # Conversation history
│   │   ├── dataset_generator.py    # JSON generation
│   │   ├── task_definitions.py     # Task configs (13 tasks)
│   │   └── orchestrator.py         # Main coordinator
│   ├── run_automation.py        # CLI entry point ⭐
│   ├── test_setup.py            # Setup validator
│   └── .env                     # Configuration (ADD YOUR API KEY HERE)
│
├── golden_dataset/              # Output directory
│   ├── dataset/                 # JSON files
│   ├── screenshots/             # VM screenshots
│   ├── terraform_code/          # Terraform code & logs
│   └── logs/                    # Automation logs
│
├── AUTOMATION_GUIDE.md          # Complete documentation
└── README.md                    # This file
```

## 🔧 Setup Instructions

### Step 1: Install Terraform

```bash
# Download Terraform
cd /tmp
wget https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip

# Extract (use unzip if available, or Python)
python3 -m zipfile -e terraform_1.6.6_linux_amd64.zip .

# Make executable and move to PATH
chmod +x terraform
sudo mv terraform /usr/local/bin/

# Verify installation
terraform --version
```

### Step 2: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 3: Configure OpenRouter API Key

Edit `/app/backend/.env`:

```bash
OPENROUTER_API_KEY=your_actual_openrouter_api_key_here
```

Get your API key from: https://openrouter.ai/keys

### Step 4: Validate Setup

```bash
cd /app/backend
python test_setup.py
```

You should see all green checkmarks ✅

## 🎯 Usage

### Run All Tasks for Both Models

```bash
cd /app/backend
python run_automation.py --all
```

This will:
- Run all 13 tasks
- Test both DeepSeek R1 and Google Gemini 3 Pro
- Generate 26 JSON dataset entries (13 tasks × 2 models)
- Capture screenshots for each task
- Save all logs and Terraform code

### Run Specific Tasks

```bash
# Single task
python run_automation.py --tasks c1_2

# Multiple tasks
python run_automation.py --tasks c1_2 c1_3 c2_2

# Specific task for specific model
python run_automation.py --models deepseek_r1 --tasks c1_2
```

### Run for One Model Only

```bash
# DeepSeek R1 only
python run_automation.py --models deepseek_r1 --all

# Google Gemini 3 Pro only
python run_automation.py --models google_gemini_3_pro --all
```

### Custom Iteration Limit

```bash
# Limit to 10 iterations per task
python run_automation.py --all --max-iterations 10
```

### Get Help

```bash
python run_automation.py --help
```

## 📊 Expected Output

After running, you'll have:

### JSON Dataset Files (26 total)
```
/app/golden_dataset/dataset/
├── deepseek_r1/
│   ├── c1_2_deepseek_r1_20250128_143022.json
│   ├── c1_3_deepseek_r1_20250128_144501.json
│   └── ... (11 more)
└── google_gemini_3_pro/
    ├── c1_2_google_gemini_3_pro_20250128_143500.json
    └── ... (12 more)
```

### Screenshots (78+ total)
```
/app/golden_dataset/screenshots/
├── c1_2_deepseek_r1_xo_list.png
├── c1_2_deepseek_r1_vm_details.png
├── c1_2_deepseek_r1_resources.png
└── ... (75+ more)
```

### Terraform Code & Logs
```
/app/golden_dataset/terraform_code/
├── deepseek_r1/
│   ├── c1_2/
│   │   ├── main.tf
│   │   ├── init.log
│   │   ├── validate.log
│   │   ├── plan.log
│   │   ├── apply.log
│   │   ├── llm_response.txt
│   │   └── conversation_history.json
│   └── ... (12 more tasks)
└── google_gemini_3_pro/
    └── ... (13 tasks)
```

## 📋 Task List

| ID | Description | Type | VMs | Depends On | Cleanup |
|----|-------------|------|-----|------------|---------|
| c1_2 | Single VM - Little Context | CREATE | 1 | - | Yes |
| c1_3 | Single VM - Detailed | CREATE | 1 | - | No* |
| c2_2 | Multiple VMs - Little Context | CREATE | 3 | - | Yes |
| c2_3 | Multiple VMs - Detailed | CREATE | 3 | - | No* |
| r1_2 | List Existing VMs | READ | 3 | c2_3 | No |
| u1_2 | Increase RAM | UPDATE | 1 | c1_3 | No* |
| d1_2 | Delete Single VM | DELETE | 0 | u1_2 | Yes |
| d2_2 | Delete Multiple VMs | DELETE | 1 | r1_2 | Yes |
| c4_2 | Incremental Addition | CREATE | 4 | c2_3 | Yes |
| c5_2 | Over-Provisioning Edge Case | CREATE | 0 | - | Yes |

*Kept for dependent tasks

## 🔍 Monitoring Progress

### Watch Real-Time Logs

```bash
tail -f /app/golden_dataset/logs/automation.log
```

### Check Task Status

The CLI shows real-time progress:
```
================================================================================
  Golden Dataset Generator for LLM Terraform Testing
================================================================================
  Base Directory: /app/golden_dataset
  Max Iterations: 20
  Models: all
  Tasks: all
================================================================================

Starting tasks for model: DeepSeek R1
============================================================

Task: C1.2 - Single VM with 2GB RAM - Little Context
============================================================

--- Iteration 1/20 ---
Calling LLM...
Extracting Terraform code...
Executing Terraform workflow...
Running terraform init...
✅ Terraform init succeeded!
Running terraform validate...
✅ Terraform validate succeeded!
Running terraform plan...
✅ Terraform plan succeeded!
Running terraform apply...
✅ Terraform apply succeeded!
Capturing screenshots...
Generating dataset entry...
✅ Task C1.2 completed successfully
```

## 🐛 Troubleshooting

### API Key Error
```bash
# Check if key is set
grep OPENROUTER_API_KEY /app/backend/.env

# Test API manually
export OPENROUTER_API_KEY="your_key"
curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Terraform Not Found
```bash
# Check installation
which terraform
terraform --version

# If not found, install (see Step 1)
```

### Playwright Issues
```bash
# Reinstall browsers
playwright install chromium

# Test Playwright
python3 -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"
```

### Xen Orchestra Not Accessible
```bash
# Test connectivity
curl http://localhost:8080

# Check if XO is running
# Verify credentials in .env match your XO setup
```

## 📈 Performance

- **Single Task**: ~3-10 minutes (depends on iterations)
- **All Tasks (1 Model)**: ~1-2 hours
- **All Tasks (Both Models)**: ~2-4 hours
- **Max Iterations**: 20 (configurable)
- **Memory Usage**: ~500MB per task

## 🎓 Advanced Usage

### Custom Task Order

Edit `/app/backend/automation/task_definitions.py`:

```python
TASK_ORDER = [
    "c1_2",
    "c1_3",
    # ... customize order
]
```

### Add New Model

Edit `/app/backend/automation/orchestrator.py`:

```python
self.models["new_model"] = {
    "full_name": "New Model Name",
    "api_id": "provider/model-id",
    "short_name": "new_model"
}
```

### Modify Platform Context

Edit `/app/backend/automation/task_definitions.py`:

```python
PLATFORM_CONTEXT = """
Your custom platform details here...
"""
```

## 📚 Documentation

- **Complete Guide**: `/app/AUTOMATION_GUIDE.md`
- **Code Comments**: All modules well-documented
- **Task Definitions**: `/app/backend/automation/task_definitions.py`
- **JSON Schema**: Generated files follow spec exactly

## ✨ Key Features

### 1. Iterative Error Handling
- LLM gets full error feedback with logs
- Maintains conversation memory
- Learns from previous attempts
- Max 20 iterations (configurable)

### 2. Task Dependencies
- Smart execution order
- VMs kept for dependent tasks
- Automatic cleanup when safe

### 3. Comprehensive Logging
- Every Terraform command logged
- Full LLM responses saved
- Conversation history preserved
- Screenshots captured

### 4. JSON Dataset Schema
- Follows specification exactly
- Includes all required fields
- Special handling for updates, incremental, edge cases
- Validation checklists included

### 5. Memory Management
- Isolated per task
- No cross-task contamination
- Conversation replay possible
- Iteration tracking

## 🎯 Success Criteria

The system will generate:

✅ **26 JSON Files** (13 tasks × 2 models)
✅ **78+ Screenshots** (3 per task × 13 × 2)
✅ **26 Terraform Directories** with code and logs
✅ **Complete Conversation Histories** for debugging
✅ **Comprehensive Automation Log**

## 🔐 Security Notes

- API keys stored in .env (not committed to git)
- Xen Orchestra credentials in .env
- Terraform state files contain sensitive data
- Screenshots may show infrastructure details

## 📞 Support

For issues:
1. Run `python test_setup.py` to validate setup
2. Check `/app/golden_dataset/logs/automation.log`
3. Review individual task logs in terraform_code directories
4. Verify Xen Orchestra is accessible
5. Check OpenRouter API key has credits

## 🏁 Ready to Start!

```bash
# 1. Install Terraform (if needed)
# 2. Install Playwright browsers
playwright install chromium

# 3. Configure API key in /app/backend/.env
nano /app/backend/.env

# 4. Validate setup
cd /app/backend
python test_setup.py

# 5. Run automation!
python run_automation.py --all
```

**Happy Testing! 🚀**
