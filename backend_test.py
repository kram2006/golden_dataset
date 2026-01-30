#!/usr/bin/env python3
"""
Backend API Testing for Automation System
Tests all automation endpoints as specified in the review request
"""

import requests
import json
import sys
from typing import Dict, Any, List
import time

# Backend URL from frontend/.env
BACKEND_URL = "https://openrouter-console.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AutomationAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = []
        
    def log_result(self, endpoint: str, method: str, success: bool, status_code: int, 
                   response_data: Any = None, error: str = None):
        """Log test result"""
        result = {
            'endpoint': endpoint,
            'method': method,
            'success': success,
            'status_code': status_code,
            'response_data': response_data,
            'error': error
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {endpoint} - Status: {status_code}")
        if error:
            print(f"   Error: {error}")
        if response_data and isinstance(response_data, dict):
            print(f"   Response keys: {list(response_data.keys())}")
        print()
    
    def test_basic_health_check(self):
        """Test GET /api/ - Basic health check"""
        print("🔍 Testing Basic Health Check...")
        try:
            response = self.session.get(f"{API_BASE}/")
            success = response.status_code == 200
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            
            if success and isinstance(data, dict) and data.get('message') == 'Hello World':
                self.log_result("/", "GET", True, response.status_code, data)
            else:
                self.log_result("/", "GET", False, response.status_code, data, 
                              f"Expected 'Hello World' message, got: {data}")
                
        except Exception as e:
            self.log_result("/", "GET", False, 0, None, str(e))
    
    def test_configuration_endpoints(self):
        """Test configuration endpoints"""
        print("🔍 Testing Configuration Endpoints...")
        
        # Test GET /api/automation/config
        try:
            response = self.session.get(f"{API_BASE}/automation/config")
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                # Check expected fields
                expected_fields = ['has_api_key', 'xo_url', 'xo_username']
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    self.log_result("/automation/config", "GET", False, response.status_code, data,
                                  f"Missing fields: {missing_fields}")
                else:
                    self.log_result("/automation/config", "GET", True, response.status_code, data)
            else:
                self.log_result("/automation/config", "GET", False, response.status_code, data,
                              f"Failed to get config")
                
        except Exception as e:
            self.log_result("/automation/config", "GET", False, 0, None, str(e))
        
        # Test POST /api/automation/config with dummy API key
        try:
            test_config = {
                "openrouter_api_key": "sk-or-test-dummy-key-12345678901234567890",
                "xo_url": "http://localhost:8080",
                "xo_username": "admin@admin.net"
            }
            
            response = self.session.post(f"{API_BASE}/automation/config", 
                                       json=test_config)
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and isinstance(data, dict) and data.get('success'):
                self.log_result("/automation/config", "POST", True, response.status_code, data)
            else:
                self.log_result("/automation/config", "POST", False, response.status_code, data,
                              f"Config update failed")
                
        except Exception as e:
            self.log_result("/automation/config", "POST", False, 0, None, str(e))
    
    def test_models_and_tasks_endpoints(self):
        """Test models and tasks endpoints"""
        print("🔍 Testing Models and Tasks Endpoints...")
        
        # Test GET /api/automation/models
        try:
            response = self.session.get(f"{API_BASE}/automation/models")
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                if isinstance(data, dict) and 'models' in data and isinstance(data['models'], list):
                    models_count = len(data['models'])
                    self.log_result("/automation/models", "GET", True, response.status_code, 
                                  {'models_count': models_count, 'sample_models': data['models'][:3]})
                else:
                    self.log_result("/automation/models", "GET", False, response.status_code, data,
                                  "Response should contain 'models' array")
            else:
                self.log_result("/automation/models", "GET", False, response.status_code, data,
                              "Failed to get models")
                
        except Exception as e:
            self.log_result("/automation/models", "GET", False, 0, None, str(e))
        
        # Test GET /api/automation/tasks
        try:
            response = self.session.get(f"{API_BASE}/automation/tasks")
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                if isinstance(data, dict) and 'tasks' in data and isinstance(data['tasks'], list):
                    tasks_count = len(data['tasks'])
                    self.log_result("/automation/tasks", "GET", True, response.status_code,
                                  {'tasks_count': tasks_count, 'tasks': data['tasks']})
                else:
                    self.log_result("/automation/tasks", "GET", False, response.status_code, data,
                                  "Response should contain 'tasks' array")
            else:
                self.log_result("/automation/tasks", "GET", False, response.status_code, data,
                              "Failed to get tasks")
                
        except Exception as e:
            self.log_result("/automation/tasks", "GET", False, 0, None, str(e))
    
    def test_results_endpoints(self):
        """Test results endpoints"""
        print("🔍 Testing Results Endpoints...")
        
        # Test GET /api/automation/logs?lines=50
        try:
            response = self.session.get(f"{API_BASE}/automation/logs?lines=50")
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                if isinstance(data, dict) and 'logs' in data and isinstance(data['logs'], list):
                    logs_count = len(data['logs'])
                    self.log_result("/automation/logs", "GET", True, response.status_code,
                                  {'logs_count': logs_count})
                else:
                    self.log_result("/automation/logs", "GET", False, response.status_code, data,
                                  "Response should contain 'logs' array")
            else:
                self.log_result("/automation/logs", "GET", False, response.status_code, data,
                              "Failed to get logs")
                
        except Exception as e:
            self.log_result("/automation/logs", "GET", False, 0, None, str(e))
        
        # Test GET /api/automation/datasets
        try:
            response = self.session.get(f"{API_BASE}/automation/datasets")
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                if isinstance(data, dict) and 'datasets' in data and isinstance(data['datasets'], list):
                    datasets_count = len(data['datasets'])
                    self.log_result("/automation/datasets", "GET", True, response.status_code,
                                  {'datasets_count': datasets_count})
                else:
                    self.log_result("/automation/datasets", "GET", False, response.status_code, data,
                                  "Response should contain 'datasets' array")
            else:
                self.log_result("/automation/datasets", "GET", False, response.status_code, data,
                              "Failed to get datasets")
                
        except Exception as e:
            self.log_result("/automation/datasets", "GET", False, 0, None, str(e))
        
        # Test GET /api/automation/screenshots
        try:
            response = self.session.get(f"{API_BASE}/automation/screenshots")
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                if isinstance(data, dict) and 'screenshots' in data and isinstance(data['screenshots'], list):
                    screenshots_count = len(data['screenshots'])
                    self.log_result("/automation/screenshots", "GET", True, response.status_code,
                                  {'screenshots_count': screenshots_count})
                else:
                    self.log_result("/automation/screenshots", "GET", False, response.status_code, data,
                                  "Response should contain 'screenshots' array")
            else:
                self.log_result("/automation/screenshots", "GET", False, response.status_code, data,
                              "Failed to get screenshots")
                
        except Exception as e:
            self.log_result("/automation/screenshots", "GET", False, 0, None, str(e))
    
    def test_cors_functionality(self):
        """Test CORS headers"""
        print("🔍 Testing CORS Functionality...")
        try:
            # Test preflight request
            response = self.session.options(f"{API_BASE}/automation/config",
                                          headers={
                                              'Origin': 'https://openrouter-console.preview.emergentagent.com',
                                              'Access-Control-Request-Method': 'GET',
                                              'Access-Control-Request-Headers': 'Content-Type'
                                          })
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            cors_working = any(cors_headers.values())
            
            self.log_result("/automation/config", "OPTIONS", cors_working, response.status_code,
                          cors_headers, None if cors_working else "No CORS headers found")
            
        except Exception as e:
            self.log_result("/automation/config", "OPTIONS", False, 0, None, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Backend API Tests for Automation System")
        print("=" * 60)
        print(f"Testing against: {API_BASE}")
        print("=" * 60)
        
        # Run all test suites
        self.test_basic_health_check()
        self.test_configuration_endpoints()
        self.test_models_and_tasks_endpoints()
        self.test_results_endpoints()
        self.test_cors_functionality()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['method']} {result['endpoint']} - {result['error']}")
        
        print("\n" + "=" * 60)
        return passed_tests, failed_tests

def main():
    """Main test runner"""
    tester = AutomationAPITester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()