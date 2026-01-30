# 🚀 Golden Dataset Automation System - How to Run

## Overview

This system provides a web-based UI to configure and monitor the automated testing of LLMs (Language Learning Models) on Terraform VM provisioning tasks with Xen Orchestra.

## 📋 Prerequisites

Before running the automation, ensure you have:

1. **OpenRouter API Key** - Get it from https://openrouter.ai/keys
2. **Xen Orchestra** - Running and accessible (default: http://localhost:8080)
3. **Terraform** - Installed and in PATH (check with `terraform --version`)
4. **Playwright** - Browser installed for screenshots

## 🎯 Quick Start Guide

### Step 1: Access the Application

The application is now running! Open your browser and navigate to your frontend URL.

### Step 2: Configure API Key

1. Click on **"Configuration"** in the navigation menu
2. Enter your **OpenRouter API Key** in the API key field
3. (Optional) Configure Xen Orchestra settings if different from defaults:
   - XO URL: `http://localhost:8080`
   - Username: `admin@admin.net`
   - Password: `admin`
4. Click **"Save Configuration"**

Your API key will be saved to `/app/backend/.env` file.

### Step 3: Run Automation

1. Go to the **"Dashboard"** page
2. In the Configuration panel:
   - **Select Models**: Choose one or more OpenRouter models to test
     - Examples: `deepseek/deepseek-r1`, `google/gemini-pro-1.5`, `anthropic/claude-3.5-sonnet`
     - You can select multiple models - the system will test each one
   - **Select Tasks**: Choose specific tasks or leave "All Tasks" selected
     - All Tasks: Runs all 13 predefined VM provisioning tasks
     - Specific: Select individual tasks like `c1_2`, `c1_3`, etc.
   - **Max Iterations**: Set how many retry attempts allowed per task (default: 20)
3. Click **"Start Automation"**

### Step 4: Monitor Progress

The Dashboard provides real-time monitoring:

**Live Logs Tab:**
- Shows real-time automation logs
- Updates every 3 seconds while running
- Green terminal-style display

**Run History Tab:**
- Shows all previous automation runs
- Status indicators (running, completed, failed)
- Success/failure counts per run

**Current Run Card:**
- Shows active run details
- Progress tracking
- Task completion counts

### Step 5: View Results

1. Go to the **"Results"** page
2. Two tabs available:

**Datasets Tab:**
- Lists all generated JSON dataset files
- Shows model, task, file size, timestamp
- Click "Download" to get the JSON file
- Each file follows the golden dataset schema

**Screenshots Tab:**
- Grid view of all captured screenshots
- Shows VM lists, details, and resource usage
- Click any image to view full size
- Organized by model and task

## 📁 Output Structure

All generated files are saved in `/app/golden_dataset/`:

```
/app/golden_dataset/
├── dataset/
│   ├── deepseek_deepseek-r1/
│   │   └── c1_2_deepseek_deepseek-r1_20250125_143022.json
│   ├── google_gemini-pro-1_5/
│   │   └── c1_2_google_gemini-pro-1_5_20250125_143545.json
│   └── ...
│
├── screenshots/
│   ├── c1_2_deepseek_deepseek-r1_xo_list.png
│   ├── c1_2_deepseek_deepseek-r1_vm_details.png
│   ├── c1_2_deepseek_deepseek-r1_resources.png
│   └── ...
│
├── terraform_code/
│   ├── deepseek_deepseek-r1/
│   │   ├── c1_2/
│   │   │   ├── main.tf
│   │   │   ├── init.log
│   │   │   ├── validate.log
│   │   │   ├── plan.log
│   │   │   ├── apply.log
│   │   │   ├── destroy.log
│   │   │   ├── llm_response.txt
│   │   │   └── conversation_history.json
│   │   └── ...
│   └── ...
│
└── logs/
    └── automation.log
```

## 🔧 API Endpoints Reference

The system exposes these REST API endpoints:

### Configuration
- `GET /api/automation/config` - Get current configuration
- `POST /api/automation/config` - Update configuration

### Models & Tasks
- `GET /api/automation/models` - Get available OpenRouter models
- `GET /api/automation/tasks` - Get available task IDs

### Automation Control
- `POST /api/automation/start` - Start automation
- `GET /api/automation/runs` - List all runs
- `GET /api/automation/runs/{run_id}` - Get specific run status
- `POST /api/automation/runs/{run_id}/cancel` - Cancel a run

### Results
- `GET /api/automation/logs?lines=100` - Get recent logs
- `GET /api/automation/datasets` - List all datasets
- `GET /api/automation/datasets/{model}/{filename}` - Download dataset
- `GET /api/automation/screenshots` - List all screenshots
- `GET /api/screenshots/{filename}` - Get screenshot image

## 🎓 Available Tasks

The system includes 13 predefined tasks:

### CREATE Operations (6 tasks)
- **c1_2**: Single VM with 2GB RAM (minimal context)
- **c1_3**: Single VM with detailed specs (app-01)
- **c2_2**: 3 identical Ubuntu VMs (minimal context)
- **c2_3**: 3 named VMs with idempotency test (web-01/02/03)
- **c4_2**: Incremental VM addition (web-04)
- **c5_2**: Over-provisioning edge case

### READ Operations (1 task)
- **r1_2**: List existing VMs and their RAM

### UPDATE Operations (1 task)
- **u1_2**: Increase RAM of app-01 from 4GB to 6GB

### DELETE Operations (2 tasks)
- **d1_2**: Delete single VM (app-01)
- **d2_2**: Delete multiple VMs (web-02, web-03)

## 💡 Tips for Best Results

### Model Selection
- Start with 1-2 models for testing
- Different models have different strengths
- Popular choices:
  - `deepseek/deepseek-r1` - Good for reasoning
  - `google/gemini-pro-1.5` - Fast and reliable
  - `anthropic/claude-3.5-sonnet` - Excellent code generation
  - `openai/gpt-4-turbo` - High quality outputs

### Task Selection
- For first run: Try just 1-2 tasks (e.g., `c1_2`, `c1_3`)
- Full run of all tasks takes 1-2 hours per model
- Tasks have dependencies (system handles automatically)

### Iteration Settings
- Default 20 iterations is usually sufficient
- Lower (5-10) for quick tests
- Higher (30-50) for difficult tasks

### Monitoring
- Keep the Dashboard open to monitor progress
- Check logs for detailed execution information
- System automatically saves all state - safe to close browser

## 🔍 Troubleshooting

### "No API key configured" Error
- Go to Configuration page
- Enter your OpenRouter API key
- Click Save Configuration
- Verify green success message appears

### Models Not Loading
- Check internet connection
- OpenRouter API must be accessible
- If API fails, default models will be shown

### Automation Not Starting
- Verify API key is configured
- Check backend logs: `tail -f /app/golden_dataset/logs/automation.log`
- Ensure Terraform is installed: `terraform --version`
- Verify XO is accessible: `curl http://localhost:8080`

### No Screenshots Captured
- Playwright must be installed: `playwright install chromium`
- XO credentials must be correct
- Check XO is running and accessible

### Tasks Failing
- Review logs in Dashboard for error details
- Check specific task logs in `/app/golden_dataset/terraform_code/`
- Verify Terraform provider is properly configured
- Ensure sufficient system resources

## 📊 Understanding Results

### Dataset JSON Files
Each JSON file contains:
- **metadata**: Model info, timestamp, infrastructure state
- **scenario**: Server resources, task requirements
- **prompt**: Exact input given to LLM
- **llm_response**: Generated code, questions, iterations
- **execution_results**: Terraform init, validate, plan, apply results
- **verification**: VM details, validation checks
- **final_outcome**: Success metrics, iterations needed
- **validation_checklist**: Code quality checks
- **screenshots**: Paths to captured images

### Screenshots
Three types per task:
1. **xo_list**: VM list view from XO dashboard
2. **vm_details**: Detailed VM information
3. **resources**: Resource usage and allocation

## 🚦 System Status

Check service status:
```bash
sudo supervisorctl status
```

Expected output:
```
backend                          RUNNING
frontend                         RUNNING
mongodb                          RUNNING
```

## 📝 Manual CLI Usage (Alternative)

You can also run automation from command line:

```bash
cd /app/backend

# Single task with one model
python run_automation.py --tasks c1_2 --models deepseek/deepseek-r1

# Multiple tasks
python run_automation.py --tasks c1_2 c1_3 c2_2

# All tasks for all configured models
python run_automation.py --all

# Custom iteration limit
python run_automation.py --tasks c1_2 --max-iterations 10
```

## 🎯 What Gets Tested

For each model and task combination, the system:

1. ✅ Sends task prompt to LLM
2. ✅ Extracts Terraform code from response
3. ✅ Executes: terraform init, validate, plan
4. ✅ If errors: Sends feedback to LLM (up to max iterations)
5. ✅ On success: Executes terraform apply
6. ✅ Captures screenshots from Xen Orchestra
7. ✅ Generates comprehensive JSON dataset
8. ✅ Saves all logs and code
9. ✅ Cleans up resources (if no dependent tasks)

## 📈 Performance Expectations

- **Single Task**: 3-10 minutes (depends on iterations needed)
- **All Tasks (1 Model)**: 1-2 hours
- **All Tasks (2 Models)**: 2-4 hours
- **All Tasks (5 Models)**: 5-10 hours

Progress is continuously saved - you can stop and resume anytime.

## 🔐 Security Notes

- API keys stored in `/app/backend/.env`
- Never commit `.env` file to version control
- XO credentials saved in same file
- All data stays on your server
- No external data sharing

## 🎉 Success Indicators

Your automation is working when you see:

✅ Configuration page shows green "API key configured" alert
✅ Dashboard loads available models
✅ "Start Automation" button works without errors
✅ Live logs show Terraform execution output
✅ Results page populates with datasets and screenshots
✅ Downloaded JSON files follow the schema
✅ Screenshots show actual VM information from XO

---

**Need Help?**
- Check logs: `/app/golden_dataset/logs/automation.log`
- Review task outputs in `/app/golden_dataset/terraform_code/`
- Verify prerequisites are met
- Test XO connection manually

**Happy Testing! 🚀**
