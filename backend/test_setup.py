#!/usr/bin/env python3
"""Test and validate the automation setup"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_color(status):
    """Return colored status"""
    return "✅" if status else "❌"

def main():
    print("\n" + "="*80)
    print("  Golden Dataset Automation - Setup Validation")
    print("="*80 + "\n")
    
    all_ok = True
    
    # Load .env
    load_dotenv(Path(__file__).parent / '.env')
    
    # 1. Check Python dependencies
    print("1. Checking Python Dependencies...")
    required_packages = ['requests', 'playwright', 'dotenv']
    for package in required_packages:
        try:
            __import__(package)
            print(f"   {check_color(True)} {package}")
        except ImportError:
            print(f"   {check_color(False)} {package} - NOT INSTALLED")
            all_ok = False
    
    # 2. Check Terraform
    print("\n2. Checking Terraform...")
    terraform_installed = subprocess.run(
        ['which', 'terraform'],
        capture_output=True
    ).returncode == 0
    
    if terraform_installed:
        result = subprocess.run(
            ['terraform', '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.split('\n')[0] if result.returncode == 0 else "unknown"
        print(f"   {check_color(True)} Terraform installed: {version}")
    else:
        print(f"   {check_color(False)} Terraform NOT INSTALLED")
        print("   Install: wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip")
        all_ok = False
    
    # 3. Check OpenRouter API Key
    print("\n3. Checking OpenRouter API Key...")
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key and api_key != '':
        print(f"   {check_color(True)} API Key configured")
    else:
        print(f"   {check_color(False)} API Key NOT configured")
        print("   Set OPENROUTER_API_KEY in /app/backend/.env")
        all_ok = False
    
    # 4. Check Xen Orchestra connectivity
    print("\n4. Checking Xen Orchestra Connectivity...")
    xo_url = os.getenv('XO_URL', 'http://localhost:8080')
    try:
        import requests
        response = requests.get(xo_url, timeout=5)
        if response.status_code in [200, 301, 302]:
            print(f"   {check_color(True)} Xen Orchestra accessible at {xo_url}")
        else:
            print(f"   {check_color(False)} Xen Orchestra returned status {response.status_code}")
            all_ok = False
    except Exception as e:
        print(f"   {check_color(False)} Cannot connect to Xen Orchestra: {str(e)}")
        print("   Make sure XO is running at localhost:8080")
        all_ok = False
    
    # 5. Check directories
    print("\n5. Checking Directory Structure...")
    required_dirs = [
        '/app/golden_dataset',
        '/app/golden_dataset/dataset',
        '/app/golden_dataset/screenshots',
        '/app/golden_dataset/terraform_code',
        '/app/golden_dataset/logs'
    ]
    
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print(f"   {check_color(exists)} {dir_path}")
        if not exists:
            all_ok = False
    
    # 6. Check automation modules
    print("\n6. Checking Automation Modules...")
    modules = [
        'automation.openrouter_client',
        'automation.terraform_executor',
        'automation.xen_screenshot',
        'automation.memory_manager',
        'automation.dataset_generator',
        'automation.task_definitions',
        'automation.orchestrator'
    ]
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    for module in modules:
        try:
            __import__(module)
            print(f"   {check_color(True)} {module}")
        except ImportError as e:
            print(f"   {check_color(False)} {module} - {str(e)}")
            all_ok = False
    
    # 7. Check Playwright
    print("\n7. Checking Playwright...")
    try:
        from playwright.sync_api import sync_playwright
        print(f"   {check_color(True)} Playwright installed")
        
        # Check if browsers are installed
        playwright_result = subprocess.run(
            ['playwright', 'install', '--help'],
            capture_output=True
        )
        if playwright_result.returncode == 0:
            print(f"   {check_color(True)} Playwright CLI available")
            print("   Run: playwright install chromium (if not already done)")
        else:
            print(f"   {check_color(False)} Playwright CLI not available")
    except ImportError:
        print(f"   {check_color(False)} Playwright not installed")
        print("   Install: pip install playwright && playwright install chromium")
        all_ok = False
    
    # Summary
    print("\n" + "="*80)
    if all_ok:
        print("✅ All checks passed! Ready to run automation.")
        print("\nQuick Start:")
        print("  1. Set your OpenRouter API key in /app/backend/.env")
        print("  2. Run: cd /app/backend && python run_automation.py --help")
        print("  3. Run all tasks: python run_automation.py --all")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nNext Steps:")
        print("  1. Install missing dependencies")
        print("  2. Configure API key in .env")
        print("  3. Ensure Xen Orchestra is accessible")
        print("  4. Re-run: python test_setup.py")
    print("="*80 + "\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
