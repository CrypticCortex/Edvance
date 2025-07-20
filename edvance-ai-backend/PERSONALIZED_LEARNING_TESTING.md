# 🎯 Personalized Learning System Testing Guide

This guide provides comprehensive test scenarios for the personalized learning path system, including API endpoints, data flows, and expected behaviors.

## 📋 System Overview

The personalized learning system consists of:
1. **Assessment Analysis** - Analyzes student performance and identifies knowledge gaps
2. **Learning Path Generation** - Creates personalized learning sequences based on gaps
3. **Progress Tracking** - Monitors student advancement through learning paths
4. **Adaptive Learning** - Modifies paths based on new assessment data

## 🚀 Quick Test Commands

### Test Assessment Analysis
```bash
# Test the system that was just demonstrated
python test_personalized_learning.py
```

### Start the FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```

## 📊 API Testing Scenarios

### 1. Assessment Analysis Testing

#### 1.1 Basic Assessment Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/personalized-learning/analyze-assessment" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_id": "test_student_123",
    "assessment_id": "grade5_math_assessment",
    "student_answers": [0, 0, 1, 1],
    "time_taken_minutes": 25
  }'
```

**Expected Response:**
```json
{
  "performance_id": "perf_xxx",
  "student_id": "test_student_123",
  "overall_score": 50.0,
  "topic_scores": {
    "Addition": 0,
    "Multiplication": 100,
    "Geometry": 0,
    "Fractions": 100
  },
  "strengths": ["Multiplication", "Fractions"],
  "weaknesses": ["Addition", "Geometry"],
  "analysis_completed": true
}
```

#### 1.2 Perfect Score Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/personalized-learning/analyze-assessment" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_id": "excellent_student_456",
    "assessment_id": "grade5_math_assessment",
    "student_answers": [1, 1, 1, 1],
    "time_taken_minutes": 15
  }'
```

#### 1.3 Poor Performance Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/personalized-learning/analyze-assessment" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_id": "struggling_student_789",
    "assessment_id": "grade5_math_assessment",
    "student_answers": [0, 0, 0, 0],
    "time_taken_minutes": 35
  }'
```

### 2. Learning Path Generation Testing

#### 2.1 Generate Path for Struggling Student
```bash
curl -X POST "http://localhost:8000/api/v1/personalized-learning/generate-learning-path" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_id": "struggling_student_789",
    "target_subject": "Mathematics",
    "target_grade": 5,
    "learning_goals": [
      "Master basic addition",
      "Understand multiplication concepts",
      "Build confidence in problem solving"
    ],
    "include_recent_assessments": 3
  }'
```

**Expected Response:**
```json
{
  "path_id": "path_xxx",
  "title": "Personalized Mathematics Learning Path",
  "total_steps": 8-12,
  "estimated_duration_hours": 4-8,
  "learning_goals": ["Master basic addition", "..."],
  "addresses_gaps": 2-4,
  "steps_preview": [
    {
      "step_number": 1,
      "title": "Basic Number Recognition",
      "topic": "Addition",
      "difficulty": "beginner",
      "estimated_minutes": 20
    }
  ],
  "path_created": true
}
```

#### 2.2 Generate Path for Advanced Student
```bash
curl -X POST "http://localhost:8000/api/v1/personalized-learning/generate-learning-path" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "student_id": "excellent_student_456",
    "target_subject": "Mathematics",
    "target_grade": 6,
    "learning_goals": [
      "Advanced problem solving",
      "Multi-step word problems",
      "Mathematical reasoning"
    ],
    "include_recent_assessments": 2
  }'
```

### 3. Progress Tracking Testing

#### 3.1 Get Student Progress
```bash
curl -X GET "http://localhost:8000/api/v1/personalized-learning/student/test_student_123/progress" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3.2 Get Learning Path Details
```bash
curl -X GET "http://localhost:8000/api/v1/personalized-learning/learning-path/{path_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3.3 Update Learning Step Progress
```bash
curl -X POST "http://localhost:8000/api/v1/personalized-learning/learning-path/{path_id}/update-progress" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "step_id": "step_xxx",
    "completed": true,
    "performance_score": 85.5
  }'
```

### 4. Adaptive Learning Testing

#### 4.1 Adapt Path Based on New Assessment
```bash
curl -X POST "http://localhost:8000/api/v1/personalized-learning/adapt-learning-path/{path_id}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "new_assessment_id": "follow_up_assessment",
    "student_answers": [1, 1, 0, 1],
    "time_taken_minutes": 20
  }'
```

## 🧪 Python Test Script

Create a comprehensive test script:

```python
# FILE: test_personalized_learning_api.py

import requests
import json
from datetime import datetime

class PersonalizedLearningTester:
    def __init__(self, base_url="http://localhost:8000", token="test_token"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    def test_assessment_analysis(self):
        """Test assessment analysis endpoint"""
        print("🧪 Testing Assessment Analysis...")
        
        test_cases = [
            {
                "name": "Mixed Performance",
                "data": {
                    "student_id": "mixed_student_001",
                    "assessment_id": "grade5_math_assessment",
                    "student_answers": [0, 1, 0, 1],
                    "time_taken_minutes": 25
                },
                "expected_score": 50.0
            },
            {
                "name": "Excellent Performance",
                "data": {
                    "student_id": "excellent_student_002",
                    "assessment_id": "grade5_math_assessment", 
                    "student_answers": [1, 1, 1, 1],
                    "time_taken_minutes": 15
                },
                "expected_score": 100.0
            },
            {
                "name": "Poor Performance",
                "data": {
                    "student_id": "struggling_student_003",
                    "assessment_id": "grade5_math_assessment",
                    "student_answers": [0, 0, 0, 0],
                    "time_taken_minutes": 40
                },
                "expected_score": 0.0
            }
        ]
        
        for test_case in test_cases:
            print(f"  📋 {test_case['name']}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/personalized-learning/analyze-assessment",
                headers=self.headers,
                json=test_case["data"]
            )
            
            if response.status_code == 200:
                result = response.json()
                actual_score = result.get("overall_score", 0)
                
                print(f"    ✅ Score: {actual_score}% (Expected: {test_case['expected_score']}%)")
                print(f"    💪 Strengths: {len(result.get('strengths', []))} areas")
                print(f"    🎯 Weaknesses: {len(result.get('weaknesses', []))} areas")
                
                if abs(actual_score - test_case["expected_score"]) < 0.1:
                    print(f"    ✅ PASS: Score matches expected")
                else:
                    print(f"    ❌ FAIL: Score mismatch")
            else:
                print(f"    ❌ FAIL: HTTP {response.status_code}")
            
            print()
    
    def test_learning_path_generation(self):
        """Test learning path generation"""
        print("🛤️ Testing Learning Path Generation...")
        
        path_requests = [
            {
                "name": "Basic Math Recovery",
                "data": {
                    "student_id": "struggling_student_003",
                    "target_subject": "Mathematics",
                    "target_grade": 5,
                    "learning_goals": [
                        "Master basic addition",
                        "Understand subtraction",
                        "Build number sense"
                    ],
                    "include_recent_assessments": 3
                },
                "expected_min_steps": 6
            },
            {
                "name": "Advanced Math Challenge",
                "data": {
                    "student_id": "excellent_student_002",
                    "target_subject": "Mathematics", 
                    "target_grade": 6,
                    "learning_goals": [
                        "Advanced problem solving",
                        "Mathematical reasoning",
                        "Complex word problems"
                    ],
                    "include_recent_assessments": 2
                },
                "expected_min_steps": 4
            }
        ]
        
        for path_request in path_requests:
            print(f"  🎯 {path_request['name']}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/personalized-learning/generate-learning-path",
                headers=self.headers,
                json=path_request["data"]
            )
            
            if response.status_code == 200:
                result = response.json()
                total_steps = result.get("total_steps", 0)
                duration_hours = result.get("estimated_duration_hours", 0)
                
                print(f"    📚 Path ID: {result.get('path_id', 'N/A')}")
                print(f"    📖 Steps: {total_steps}")
                print(f"    ⏱️ Duration: {duration_hours:.1f} hours")
                print(f"    🎯 Addresses: {result.get('addresses_gaps', 0)} gaps")
                
                if total_steps >= path_request["expected_min_steps"]:
                    print(f"    ✅ PASS: Adequate number of steps")
                else:
                    print(f"    ❌ FAIL: Too few steps")
                    
                # Store path_id for progress testing
                if hasattr(self, 'test_path_ids'):
                    self.test_path_ids.append(result.get('path_id'))
                else:
                    self.test_path_ids = [result.get('path_id')]
                    
            else:
                print(f"    ❌ FAIL: HTTP {response.status_code}")
            
            print()
    
    def test_progress_tracking(self):
        """Test progress tracking and updates"""
        print("📈 Testing Progress Tracking...")
        
        # Test student progress summary
        print("  📊 Student Progress Summary")
        response = requests.get(
            f"{self.base_url}/api/v1/personalized-learning/student/test_student_123/progress",
            headers=self.headers
        )
        
        if response.status_code == 200:
            print("    ✅ Progress summary retrieved")
        else:
            print(f"    ❌ FAIL: HTTP {response.status_code}")
        
        # Test learning path details (if we have path IDs)
        if hasattr(self, 'test_path_ids') and self.test_path_ids:
            path_id = self.test_path_ids[0]
            print(f"  📋 Learning Path Details: {path_id[:8]}...")
            
            response = requests.get(
                f"{self.base_url}/api/v1/personalized-learning/learning-path/{path_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ Path details retrieved: {len(result.get('steps', []))} steps")
            else:
                print(f"    ❌ FAIL: HTTP {response.status_code}")
        
        print()
    
    def test_analytics(self):
        """Test analytics endpoints"""
        print("📊 Testing Analytics...")
        
        # Test teacher analytics
        print("  👨‍🏫 Teacher Analytics")
        response = requests.get(
            f"{self.base_url}/api/v1/personalized-learning/teacher/learning-analytics",
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"    ✅ Analytics retrieved")
            print(f"    📈 Recommendations: {len(result.get('recommendations_for_teacher', []))}")
        else:
            print(f"    ❌ FAIL: HTTP {response.status_code}")
        
        # Test student insights
        print("  👨‍🎓 Student Insights")
        response = requests.get(
            f"{self.base_url}/api/v1/personalized-learning/student/test_student_123/learning-insights",
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"    ✅ Insights retrieved")
            print(f"    🎯 Actions: {len(result.get('next_recommended_actions', []))}")
        else:
            print(f"    ❌ FAIL: HTTP {response.status_code}")
        
        print()
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🎯 PERSONALIZED LEARNING SYSTEM - COMPREHENSIVE TEST")
        print("=" * 60)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print()
        
        try:
            self.test_assessment_analysis()
            self.test_learning_path_generation()
            self.test_progress_tracking()
            self.test_analytics()
            
            print("🎉 ALL TESTS COMPLETED!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ TEST SUITE FAILED: {str(e)}")

if __name__ == "__main__":
    # Replace with your actual token
    tester = PersonalizedLearningTester(token="your_jwt_token_here")
    tester.run_all_tests()
```

## 🎭 Test Scenarios by Student Profile

### 1. The Struggling Student
- **Profile**: Low performance across all areas
- **Expected Path**: Basic foundational skills, lots of practice
- **Test Data**: All wrong answers (0, 0, 0, 0)

### 2. The Mixed Performer
- **Profile**: Strong in some areas, weak in others
- **Expected Path**: Targeted improvement for weak areas
- **Test Data**: Half correct (0, 1, 0, 1)

### 3. The Excellent Student
- **Profile**: High performance, ready for challenges
- **Expected Path**: Advanced content, enrichment activities
- **Test Data**: All correct (1, 1, 1, 1)

### 4. The Quick Learner
- **Profile**: Fast completion, good understanding
- **Expected Path**: Accelerated pace, complex problems
- **Test Data**: Correct answers in minimal time

### 5. The Slow but Steady
- **Profile**: Takes time but gets it right
- **Expected Path**: More time allocation, step-by-step approach
- **Test Data**: Correct answers but longer completion time

## 🔧 Debugging and Validation

### Check System Components
```bash
# 1. Verify Firebase connection
python -c "from app.core.firebase import db; print('Firebase:', 'Connected' if db else 'Failed')"

# 2. Verify Vertex AI
python -c "from app.core.vertex import gemini_model; print('Vertex AI:', 'Connected' if gemini_model else 'Failed')"

# 3. Test assessment service
python -c "from app.services.enhanced_assessment_service import enhanced_assessment_service; print('Assessment Service: Ready')"

# 4. Test analysis service
python -c "from app.services.assessment_analysis_service import assessment_analysis_service; print('Analysis Service: Ready')"
```

### Monitor Logs
```bash
# Watch application logs
tail -f app.log

# Filter for personalized learning
grep "personalized" app.log

# Check for errors
grep "ERROR" app.log | grep -i "learning\|assessment\|path"
```

## 📈 Expected Performance Metrics

### Assessment Analysis
- **Response Time**: < 2 seconds
- **Accuracy**: 95%+ score calculation
- **Gap Detection**: 80%+ accuracy for obvious gaps

### Learning Path Generation
- **Response Time**: < 5 seconds for complex paths
- **Step Count**: 5-15 steps per path
- **Personalization**: Paths should differ based on performance

### Progress Tracking
- **Update Speed**: < 1 second
- **Data Consistency**: 100% accurate progress calculation
- **Adaptation**: Path modifications within 3 seconds

## 🎯 Success Criteria

### ✅ Assessment Analysis Success
- [ ] Correctly calculates scores
- [ ] Identifies topic-specific weaknesses
- [ ] Generates actionable insights
- [ ] Stores performance data

### ✅ Learning Path Generation Success
- [ ] Creates personalized steps
- [ ] Addresses identified gaps
- [ ] Provides realistic time estimates
- [ ] Maintains logical progression

### ✅ Progress Tracking Success
- [ ] Updates completion status
- [ ] Calculates progress percentages
- [ ] Tracks performance scores
- [ ] Maintains step dependencies

### ✅ Adaptive Learning Success
- [ ] Modifies paths based on new data
- [ ] Maintains learning continuity
- [ ] Improves recommendations over time
- [ ] Responds to performance changes

## 🚨 Common Issues and Solutions

### Issue: "Assessment not found"
**Solution**: Ensure assessment exists in database before analysis

### Issue: "Empty learning path generated"
**Solution**: Check knowledge gap detection and AI prompt effectiveness

### Issue: "Progress update failed"
**Solution**: Verify step_id exists and learning path is active

### Issue: "Adaptation not working"
**Solution**: Confirm new assessment data format and gap identification

---

**🎉 Ready to test your personalized learning system!**

Run the tests and watch as the AI creates truly personalized educational experiences for each student profile.
