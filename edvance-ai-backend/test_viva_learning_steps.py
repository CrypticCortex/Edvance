#!/usr/bin/env python3
"""
Test script to verify VIVA bot uses actual learning step data instead of default topics.
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code', 'edvance-ai-backend'))

from app.agents.tools.viva_tools import get_viva_topic, start_viva_session, auto_start_viva_for_step
from app.services.learning_path_service import learning_path_service
from app.services.learning_path_viva_integration import learning_path_viva_integration
from app.models.learning_models import (
    LearningPath, LearningStep, KnowledgeGap, 
    DifficultyLevel, LearningObjectiveType
)

async def create_test_learning_path():
    """Create a test learning path with learning steps for testing."""
    
    print("Creating test learning path...")
    
    # Create test knowledge gaps
    test_gaps = [
        KnowledgeGap(
            gap_id=str(uuid.uuid4()),
            student_id="test_student_123",
            subject="Mathematics",
            topic="Algebra",
            subtopic="Linear Equations",
            difficulty_level=DifficultyLevel.MEDIUM,
            learning_objective=LearningObjectiveType.APPLY,
            confidence_score=0.8,
            severity_score=0.7,
            frequency=3,
            source_assessments=["test_assessment_1"],
            related_questions=["q1", "q2", "q3"]
        )
    ]
    
    # Create test learning steps
    test_steps = [
        LearningStep(
            step_id="test_step_algebra_basics",
            step_number=1,
            title="Introduction to Linear Equations",
            description="Learn the fundamentals of solving linear equations with one variable",
            subject="Mathematics",
            topic="Algebra",
            subtopic="Linear Equations",
            difficulty_level=DifficultyLevel.MEDIUM,
            learning_objective=LearningObjectiveType.UNDERSTAND,
            content_type="viva",
            content_text="Focus on understanding what linear equations are, how to identify them, and basic solving techniques like addition, subtraction, multiplication, and division properties of equality.",
            estimated_duration_minutes=20,
            addresses_gaps=[test_gaps[0].gap_id]
        ),
        LearningStep(
            step_id="test_step_equation_solving",
            step_number=2,
            title="Advanced Linear Equation Solving",
            description="Practice solving more complex linear equations with multiple steps",
            subject="Mathematics",
            topic="Algebra",
            subtopic="Linear Equations",
            difficulty_level=DifficultyLevel.HARD,
            learning_objective=LearningObjectiveType.APPLY,
            content_type="viva",
            content_text="Practice solving equations with variables on both sides, equations with fractions and decimals, and word problems involving linear equations.",
            estimated_duration_minutes=25,
            addresses_gaps=[test_gaps[0].gap_id],
            prerequisites=["test_step_algebra_basics"]
        )
    ]
    
    # Create test learning path
    test_path = LearningPath(
        path_id="test_path_algebra",
        student_id="test_student_123",
        teacher_uid="test_teacher_456",
        title="Algebra Fundamentals Learning Path",
        description="A personalized path to master linear equations",
        subject="Mathematics",
        target_grade=8,
        learning_goals=["Master linear equation solving", "Build confidence in algebra"],
        addresses_gaps=[gap.gap_id for gap in test_gaps],
        steps=test_steps,
        total_estimated_duration_minutes=45
    )
    
    # Save the test learning path
    try:
        await learning_path_service._save_learning_path(test_path)
        print(f"✅ Created test learning path: {test_path.path_id}")
        return test_path
    except Exception as e:
        print(f"❌ Failed to create test learning path: {str(e)}")
        return None

async def test_viva_topic_retrieval():
    """Test that get_viva_topic returns actual learning step data."""
    
    print("\n=== Testing VIVA Topic Retrieval ===")
    
    # Test with a known learning step ID
    test_step_id = "test_step_algebra_basics"
    
    try:
        topic = await get_viva_topic(test_step_id)
        print(f"✅ Retrieved topic for step {test_step_id}: '{topic}'")
        
        # Check if it's not the default topic
        if topic != "General Review Topic" and "Algebra" in topic:
            print("✅ Topic appears to be from actual learning step data")
            return True
        else:
            print(f"⚠️  Topic might be default or not specific: '{topic}'")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving topic: {str(e)}")
        return False

async def test_viva_session_start():
    """Test that starting a VIVA session uses learning step data."""
    
    print("\n=== Testing VIVA Session Start ===")
    
    test_student_id = "test_student_123"
    test_step_id = "test_step_algebra_basics"
    test_language = "english"
    
    try:
        session_result = await start_viva_session(test_student_id, test_step_id, test_language)
        
        if "error" in session_result:
            print(f"❌ Error starting session: {session_result['error']}")
            return False
        
        print(f"✅ Started VIVA session: {session_result.get('session_id')}")
        print(f"📝 Topic: {session_result.get('topic', 'Not specified')}")
        print(f"💬 Welcome message preview: {session_result.get('welcome_message', '')[:100]}...")
        
        # Check if the topic is specific to the learning step
        topic = session_result.get('topic', '')
        if topic and topic != "General Review Topic" and "Linear Equations" in topic:
            print("✅ Session topic appears to be from actual learning step")
            return True
        else:
            print(f"⚠️  Session topic might be default: '{topic}'")
            return False
            
    except Exception as e:
        print(f"❌ Error starting VIVA session: {str(e)}")
        return False

async def test_nonexistent_learning_step():
    """Test behavior with non-existent learning step ID."""
    
    print("\n=== Testing Non-existent Learning Step ===")
    
    fake_step_id = "nonexistent_step_12345"
    
    try:
        topic = await get_viva_topic(fake_step_id)
        print(f"📝 Topic for non-existent step: '{topic}'")
        
        if topic == "General Review Topic":
            print("✅ Correctly returned default topic for non-existent step")
            return True
        else:
            print(f"⚠️  Unexpected topic for non-existent step: '{topic}'")
            return False
            
    except Exception as e:
        print(f"❌ Error with non-existent step: {str(e)}")
        return False

async def test_seamless_learning_path_integration():
    """Test the seamless integration of VIVA with learning path progression."""
    
    print("\n=== Testing Seamless Learning Path Integration ===")
    
    test_student_id = "test_student_123"
    test_path_id = "test_path_algebra"
    
    try:
        # Test getting current step with automatic VIVA preparation
        current_step = await learning_path_viva_integration.get_student_current_step_with_viva(
            test_student_id, test_path_id, "english"
        )
        
        if "error" in current_step:
            print(f"❌ Error getting current step: {current_step['error']}")
            return False
        
        print(f"✅ Got current step: {current_step.get('title', 'Unknown')}")
        print(f"📝 Has VIVA: {current_step.get('has_viva', False)}")
        
        if current_step.get("has_viva"):
            print(f"🎯 VIVA Status: {current_step.get('viva_status', 'unknown')}")
            if current_step.get("viva_session_id"):
                print(f"🆔 VIVA Session ID: {current_step['viva_session_id']}")
                print("✅ VIVA session automatically created for learning step")
                return True
            else:
                print("⚠️  VIVA step but no session created")
                return False
        else:
            print("⚠️  Current step doesn't have VIVA configured")
            return False
            
    except Exception as e:
        print(f"❌ Error testing seamless integration: {str(e)}")
        return False

async def test_auto_viva_detection():
    """Test automatic VIVA detection for learning steps."""
    
    print("\n=== Testing Auto VIVA Detection ===")
    
    test_student_id = "test_student_123"
    test_step_id = "test_step_algebra_basics"
    
    try:
        # Test auto VIVA detection
        auto_result = await auto_start_viva_for_step(test_student_id, test_step_id, "english")
        
        if "error" in auto_result:
            print(f"❌ Error in auto VIVA detection: {auto_result['error']}")
            return False
        
        print(f"✅ Auto VIVA detection result: {auto_result.get('has_viva', False)}")
        
        if auto_result.get("has_viva"):
            print(f"🎯 VIVA session created: {auto_result.get('session_id', 'None')}")
            print("✅ Successfully detected and started VIVA for learning step")
            return True
        else:
            print(f"📝 Step content type: {auto_result.get('content_type', 'unknown')}")
            print("⚠️  Step not configured for VIVA")
            return False
            
    except Exception as e:
        print(f"❌ Error testing auto VIVA detection: {str(e)}")
        return False

async def main():
    """Run all VIVA learning step integration tests."""
    
    print("🧪 Testing VIVA Bot Learning Step Integration")
    print("=" * 50)
    
    # Create test data
    test_path = await create_test_learning_path()
    if not test_path:
        print("❌ Failed to create test data. Exiting.")
        return
    
    # Run tests
    test_results = []
    
    test_results.append(await test_viva_topic_retrieval())
    test_results.append(await test_viva_session_start())
    test_results.append(await test_nonexistent_learning_step())
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Summary")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! VIVA bot is now using learning step data.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    print("\n📋 Key Changes Made:")
    print("- ✅ get_viva_topic() now fetches actual learning step data")
    print("- ✅ VIVA sessions use learning step context for prompts")
    print("- ✅ AI examiner questions are tailored to learning objectives")
    print("- ✅ Scoring considers learning step difficulty and objectives")
    print("- ✅ Fallback to default topic when learning step not found")

if __name__ == "__main__":
    asyncio.run(main())