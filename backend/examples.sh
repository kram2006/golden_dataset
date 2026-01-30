#!/bin/bash

# Golden Dataset Automation - Example Usage Script
# This script demonstrates various ways to use the automation system

echo "=============================================="
echo "  Golden Dataset Automation - Examples"
echo "=============================================="
echo ""

# Set colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd /app/backend

echo -e "${BLUE}Example 1: Validate Setup${NC}"
echo "Command: python test_setup.py"
echo ""
python test_setup.py
echo ""
read -p "Press Enter to continue..."
echo ""

echo -e "${BLUE}Example 2: Show Help${NC}"
echo "Command: python run_automation.py --help"
echo ""
python run_automation.py --help
echo ""
read -p "Press Enter to continue..."
echo ""

echo -e "${BLUE}Example 3: Run Single Task for DeepSeek R1${NC}"
echo "Command: python run_automation.py --models deepseek_r1 --tasks c1_2"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  • Test DeepSeek R1 model only"
echo "  • Run task C1.2 (Single VM with 2GB RAM)"
echo "  • Create 1 JSON file"
echo "  • Capture 3 screenshots"
echo "  • Save all logs"
echo ""
read -p "Run this example? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python run_automation.py --models deepseek_r1 --tasks c1_2
fi
echo ""

echo -e "${BLUE}Example 4: Run Multiple Tasks${NC}"
echo "Command: python run_automation.py --tasks c1_2 c1_3 c2_2"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  • Test both models"
echo "  • Run 3 tasks (c1_2, c1_3, c2_2)"
echo "  • Create 6 JSON files (3 tasks × 2 models)"
echo "  • Capture 18 screenshots"
echo ""
read -p "Run this example? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python run_automation.py --tasks c1_2 c1_3 c2_2
fi
echo ""

echo -e "${BLUE}Example 5: Run All Tasks for One Model${NC}"
echo "Command: python run_automation.py --models google_gemini_3_pro --all"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  • Test Google Gemini 3 Pro only"
echo "  • Run all 13 tasks"
echo "  • Create 13 JSON files"
echo "  • Capture 39+ screenshots"
echo "  • Take approximately 1-2 hours"
echo ""
read -p "Run this example? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python run_automation.py --models google_gemini_3_pro --all
fi
echo ""

echo -e "${BLUE}Example 6: Run All Tasks for All Models${NC}"
echo "Command: python run_automation.py --all"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  • Test both DeepSeek R1 and Google Gemini 3 Pro"
echo "  • Run all 13 tasks for each model"
echo "  • Create 26 JSON files (13 tasks × 2 models)"
echo "  • Capture 78+ screenshots"
echo "  • Take approximately 2-4 hours"
echo ""
read -p "Run this example? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python run_automation.py --all
fi
echo ""

echo -e "${BLUE}Example 7: Custom Iteration Limit${NC}"
echo "Command: python run_automation.py --tasks c1_2 --max-iterations 5"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  • Run task C1.2"
echo "  • Limit to 5 retry iterations (instead of default 20)"
echo "  • Useful for faster testing"
echo ""
read -p "Run this example? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python run_automation.py --tasks c1_2 --max-iterations 5
fi
echo ""

echo -e "${GREEN}=============================================="
echo "  Examples Complete!"
echo "=============================================="
echo ""
echo "Output Locations:"
echo "  • JSON Files: /app/golden_dataset/dataset/"
echo "  • Screenshots: /app/golden_dataset/screenshots/"
echo "  • Terraform Code: /app/golden_dataset/terraform_code/"
echo "  • Logs: /app/golden_dataset/logs/automation.log"
echo ""
echo "View results:"
echo "  ls -lh /app/golden_dataset/dataset/deepseek_r1/"
echo "  ls -lh /app/golden_dataset/screenshots/"
echo "  tail -f /app/golden_dataset/logs/automation.log"
echo ""
