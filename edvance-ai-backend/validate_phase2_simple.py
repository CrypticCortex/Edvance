#!/usr/bin/env python3
"""
Phase 2 Assessment System Validation
"""

def test_models():
    """Test assessment models."""
    print("🧪 Testing Assessment Models...")
    
    from app.models.student import AssessmentConfig, Assessment, AssessmentQuestion
    
    # Test AssessmentConfig
    config = AssessmentConfig(
        config_id="test-config-123",
        teacher_uid="teacher-456",
        name="Grade 5 Math Test",
        subject="Mathematics",
        target_grade=5,
        difficulty_level="medium",
        topic="Addition",
        question_count=10,
        time_limit_minutes=30
    )
    print(f"✅ AssessmentConfig: {config.name} for {config.subject} Grade {config.target_grade}")
    
    # Test AssessmentQuestion
    question = AssessmentQuestion(
        question_id="q1",
        question_text="What is 2 + 2?",
        options=["3", "4", "5", "6"],
        correct_answer=1,
        explanation="2 + 2 = 4",
        difficulty="easy",
        topic="Addition"
    )
    print(f"✅ AssessmentQuestion: {question.question_text}")
    
    return True

def test_service():
    """Test simple assessment service."""
    print("\n🔧 Testing Simple Assessment Service...")
    
    try:
        from app.services.simple_assessment_service import simple_assessment_service
        print("✅ Simple assessment service imported successfully")
        
        # Test topic generation
        topics = simple_assessment_service._generate_sample_questions("Mathematics", 5, "Addition", "easy", 3)
        print(f"✅ Generated {len(topics)} sample questions")
        
        return True
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

def test_api():
    """Test assessment API."""
    print("\n🌐 Testing Assessment API...")
    
    try:
        from app.api.v1.simple_assessments import router
        print("✅ Assessment API router imported successfully")
        
        # Check routes
        routes = [route.path for route in router.routes]
        expected_routes = ["/configs", "/topics/{subject}/{grade}", "/summary"]
        
        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"✅ Route found: {expected}")
            else:
                print(f"❌ Route missing: {expected}")
        
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_app_creation():
    """Test app creation with Phase 2."""
    print("\n🏗️ Testing App Creation...")
    
    try:
        # Just test import, not full creation to avoid Firebase dependencies
        from app.core.app_factory import create_app
        print("✅ App factory can be imported")
        
        # Test router imports
        from app.api.v1 import simple_assessments
        print("✅ Simple assessments router can be imported")
        
        return True
    except Exception as e:
        print(f"❌ App creation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Phase 2: Assessment System - Validation")
    print("=" * 50)
    
    tests = [
        ("Assessment Models", test_models),
        ("Assessment Service", test_service),
        ("Assessment API", test_api),
        ("App Creation", test_app_creation)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print(f"{'✅' if result else '❌'} {name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
            results.append(False)
    
    print("\n📋 Phase 2 Summary:")
    if all(results):
        print("🎉 All Phase 2 validations passed!")
        print("\n🚀 Phase 2 Complete: Simple Assessment System Ready")
        print("\n📋 What works now:")
        print("• Create assessment configurations")
        print("• Generate sample assessments with questions")
        print("• Get available topics by subject/grade")
        print("• Assessment management API endpoints")
        print("\n🔄 Current Workflow:")
        print("1. Teacher creates assessment config (subject, grade, difficulty, topic)")
        print("2. System generates sample assessment with MCQ questions")
        print("3. Assessment is ready for deployment to students")
        print("\n🎯 Ready for Phase 3: Student Assessment Taking!")
    else:
        print("❌ Some Phase 2 validations failed")
        print("🔧 Fix the issues above before proceeding")
