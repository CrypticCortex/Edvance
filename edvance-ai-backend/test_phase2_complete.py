#!/usr/bin/env python3
"""
Automated Phase 2 Testing Script
Run this after starting the server to test all Phase 2 functionality
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEACHER_EMAIL = "teacher@example.com"  # Replace with real email
TEACHER_PASSWORD = "password123"       # Replace with real password

class Phase2Tester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.config_id = None
        self.assessment_id = None
        
    def print_step(self, step: int, title: str):
        print(f"\n{'='*60}")
        print(f"STEP {step}: {title}")
        print('='*60)
    
    def print_result(self, success: bool, message: str, data: Any = None):
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {message}")
        if data and isinstance(data, dict):
            print(f"📊 Data: {json.dumps(data, indent=2, default=str)[:200]}...")
        elif data:
            print(f"📊 Data: {str(data)[:200]}...")
    
    def test_health_check(self) -> bool:
        """Step 1: Health Check"""
        self.print_step(1, "Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, "Server is healthy", data)
                return True
            else:
                self.print_result(False, f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_result(False, f"Health check error: {e}")
            return False
    
    def test_authentication(self) -> bool:
        """Step 2: Authentication"""
        self.print_step(2, "Authentication")
        
        try:
            login_data = {
                "email": TEACHER_EMAIL,
                "password": TEACHER_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/v1/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("id_token")
                if self.token:
                    self.print_result(True, "Authentication successful", {"token_preview": self.token[:20] + "..."})
                    return True
                else:
                    self.print_result(False, "No token in response", data)
                    return False
            else:
                self.print_result(False, f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Authentication error: {e}")
            return False
    
    def test_get_students(self) -> bool:
        """Step 3: Get Students"""
        self.print_step(3, "Get Students")
        
        if not self.token:
            self.print_result(False, "No authentication token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/v1/students/", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, f"Retrieved {len(data)} students", {"count": len(data)})
                return True
            else:
                self.print_result(False, f"Get students failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Get students error: {e}")
            return False
    
    def test_get_topics(self) -> bool:
        """Step 4: Get Available Topics"""
        self.print_step(4, "Get Available Topics")
        
        if not self.token:
            self.print_result(False, "No authentication token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/v1/assessments/topics/Mathematics/5", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, f"Retrieved {len(data)} topics for Math Grade 5", data)
                return True
            else:
                self.print_result(False, f"Get topics failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Get topics error: {e}")
            return False
    
    def test_create_config(self) -> bool:
        """Step 5: Create Assessment Configuration"""
        self.print_step(5, "Create Assessment Configuration")
        
        if not self.token:
            self.print_result(False, "No authentication token")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            config_data = {
                "name": "Test Grade 5 Math Addition",
                "subject": "Mathematics",
                "target_grade": 5,
                "difficulty_level": "medium",
                "topic": "Addition",
                "question_count": 5,
                "time_limit_minutes": 15
            }
            
            response = requests.post(
                f"{self.base_url}/v1/assessments/configs",
                headers=headers,
                json=config_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.config_id = data.get("config_id")
                self.print_result(True, "Assessment config created", data)
                return True
            else:
                self.print_result(False, f"Create config failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Create config error: {e}")
            return False
    
    def test_generate_assessment(self) -> bool:
        """Step 6: Generate Assessment"""
        self.print_step(6, "Generate Assessment from Configuration")
        
        if not self.token or not self.config_id:
            self.print_result(False, "No authentication token or config ID")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.base_url}/v1/assessments/configs/{self.config_id}/generate",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assessment_id = data.get("assessment_id")
                question_count = len(data.get("questions", []))
                self.print_result(True, f"Assessment generated with {question_count} questions", {
                    "assessment_id": self.assessment_id,
                    "title": data.get("title"),
                    "question_count": question_count
                })
                return True
            else:
                self.print_result(False, f"Generate assessment failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Generate assessment error: {e}")
            return False
    
    def test_get_assessment(self) -> bool:
        """Step 7: Get Assessment Details"""
        self.print_step(7, "Get Assessment Details")
        
        if not self.token or not self.assessment_id:
            self.print_result(False, "No authentication token or assessment ID")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/v1/assessments/assessments/{self.assessment_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                first_question = questions[0] if questions else None
                
                self.print_result(True, f"Retrieved assessment with {len(questions)} questions", {
                    "title": data.get("title"),
                    "subject": data.get("subject"),
                    "grade": data.get("grade"),
                    "first_question": first_question.get("question_text") if first_question else None
                })
                return True
            else:
                self.print_result(False, f"Get assessment failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Get assessment error: {e}")
            return False
    
    def test_assessment_summary(self) -> bool:
        """Step 8: Get Assessment Summary"""
        self.print_step(8, "Get Assessment Summary")
        
        if not self.token:
            self.print_result(False, "No authentication token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/v1/assessments/summary",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, "Retrieved assessment summary", data)
                return True
            else:
                self.print_result(False, f"Get summary failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Get summary error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("🎯 Starting Phase 2 Assessment System Testing")
        print(f"🌐 Server: {self.base_url}")
        print(f"👤 Teacher: {TEACHER_EMAIL}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("Get Students", self.test_get_students),
            ("Get Topics", self.test_get_topics),
            ("Create Config", self.test_create_config),
            ("Generate Assessment", self.test_generate_assessment),
            ("Get Assessment", self.test_get_assessment),
            ("Assessment Summary", self.test_assessment_summary)
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append(result)
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ {name}: FAILED - {e}")
                results.append(False)
        
        # Final Summary
        print(f"\n{'='*60}")
        print("🏁 PHASE 2 TESTING SUMMARY")
        print('='*60)
        
        passed = sum(results)
        total = len(results)
        
        for i, (name, result) in enumerate(zip([t[0] for t in tests], results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{i+1}. {name}: {status}")
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Phase 2 is working perfectly!")
            print("\n🚀 Ready for Phase 3: Student Assessment Taking")
            print("\nNext steps:")
            print("• Students can now take assessments")
            print("• Implement scoring and analytics") 
            print("• Generate personalized learning paths")
        else:
            print("❌ Some tests failed. Check the logs above for details.")
            print("🔧 Fix the issues before proceeding to Phase 3.")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Update TEACHER_EMAIL and TEACHER_PASSWORD at the top of this file!")
    print("⚠️  Make sure the server is running on http://localhost:8000")
    print("\n" + "="*60)
    
    input("Press Enter to start testing (or Ctrl+C to cancel)...")
    
    tester = Phase2Tester()
    tester.run_all_tests()
