#!/usr/bin/env python3
"""
Test script to verify the complete lesson system integration.
This tests the ultra-fast lesson generation and chatbot functionality.
"""

import asyncio
import json
import time
from typing import Dict, Any

from app.agents.tools.lesson_tools import (
    generate_lesson_content,
    lesson_agent_chat,
    get_lesson_by_id
)

async def test_lesson_system():
    """Test the complete lesson system with realistic data."""
    
    print("🚀 LESSON SYSTEM INTEGRATION TEST")
    print("=" * 50)
    
    # Test data
    test_data = {
        "learning_step_id": "step_math_algebra_basics",
        "student_id": "student_test_123",
        "teacher_uid": "teacher_demo_456",
        "customizations": {
            "difficulty_adjustment": "normal",
            "focus_areas": ["basic operations", "solving equations"],
            "learning_style": "visual",
            "include_interactive": True,
            "slide_count_preference": "short"
        }
    }
    
    try:
        # Step 1: Test Ultra-Fast Lesson Generation
        print("\n📚 Step 1: Testing Ultra-Fast Lesson Generation")
        print("-" * 40)
        
        start_time = time.time()
        lesson_result = await generate_lesson_content(
            learning_step_id=test_data["learning_step_id"],
            student_id=test_data["student_id"],
            teacher_uid=test_data["teacher_uid"],
            customizations=test_data["customizations"]
        )
        generation_time = time.time() - start_time
        
        if lesson_result.get("success"):
            lesson_id = lesson_result.get("lesson_id")
            print(f"✅ Lesson generated successfully in {generation_time:.2f}s")
            print(f"📖 Lesson ID: {lesson_id}")
            print(f"🎯 Performance Target: <30s ({'✅ PASSED' if generation_time < 30 else '❌ FAILED'})")
            
            # Step 2: Test Lesson Retrieval
            print(f"\n📋 Step 2: Testing Lesson Retrieval")
            print("-" * 40)
            
            lesson_data = await get_lesson_by_id(lesson_id, test_data["student_id"])
            if lesson_data.get("success"):
                lesson_content = lesson_data.get("lesson")
                slide_count = len(lesson_content.get("slides", []))
                print(f"✅ Lesson retrieved successfully")
                print(f"📊 Slides generated: {slide_count}")
                print(f"🎯 Topic: {lesson_content.get('topic', 'N/A')}")
                print(f"⏱️ Estimated duration: {lesson_content.get('estimated_duration_minutes', 'N/A')} minutes")
                
                # Step 3: Test Chatbot Functionality
                print(f"\n🤖 Step 3: Testing Lesson Chatbot")
                print("-" * 40)
                
                test_questions = [
                    "Can you explain the main concept of this lesson?",
                    "I'm confused about slide 2. Can you help?",
                    "Give me a practice problem to test my understanding."
                ]
                
                for i, question in enumerate(test_questions, 1):
                    print(f"\n🤔 Question {i}: {question}")
                    
                    chat_start = time.time()
                    chat_result = await lesson_agent_chat(
                        lesson_id=lesson_id,
                        student_id=test_data["student_id"],
                        message=question,
                        session_id=f"test_session_{i}"
                    )
                    chat_time = time.time() - chat_start
                    
                    if chat_result.get("success"):
                        response = chat_result.get("response", "")
                        print(f"✅ Response ({chat_time:.2f}s): {response[:100]}...")
                    else:
                        print(f"❌ Chat failed: {chat_result.get('error', 'Unknown error')}")
                
                # Step 4: Performance Summary
                print(f"\n📈 INTEGRATION TEST SUMMARY")
                print("=" * 50)
                print(f"🎯 Lesson Generation: {generation_time:.2f}s ({'✅ PASSED' if generation_time < 30 else '❌ FAILED'})")
                print(f"📚 Content Quality: {'✅ PASSED' if slide_count >= 3 else '❌ FAILED'} ({slide_count} slides)")
                print(f"🤖 Chatbot: {'✅ OPERATIONAL' if chat_result.get('success') else '❌ FAILED'}")
                print(f"🚀 System Status: {'✅ PRODUCTION READY' if generation_time < 30 and slide_count >= 3 else '⚠️ NEEDS OPTIMIZATION'}")
                
            else:
                print(f"❌ Failed to retrieve lesson: {lesson_data.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ Lesson generation failed: {lesson_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Integration test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_quick_performance():
    """Quick performance test for the ultra-fast method."""
    
    print("\n⚡ QUICK PERFORMANCE VERIFICATION")
    print("=" * 40)
    
    test_data = {
        "learning_step_id": "quick_test_step",
        "student_id": "quick_test_student",
        "teacher_uid": "quick_test_teacher",
        "customizations": {"slide_count_preference": "short"}
    }
    
    runs = 3
    times = []
    
    for i in range(runs):
        print(f"🏃 Run {i+1}/{runs}...", end=" ")
        start_time = time.time()
        
        result = await generate_lesson_content(
            learning_step_id=test_data["learning_step_id"],
            student_id=test_data["student_id"],
            teacher_uid=test_data["teacher_uid"],
            customizations=test_data["customizations"]
        )
        
        run_time = time.time() - start_time
        times.append(run_time)
        
        status = "✅" if result.get("success") else "❌"
        print(f"{status} {run_time:.2f}s")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n📊 Performance Results:")
    print(f"   Average: {avg_time:.2f}s")
    print(f"   Best:    {min_time:.2f}s")
    print(f"   Worst:   {max_time:.2f}s")
    print(f"   Target:  <30.0s ({'✅ ACHIEVED' if avg_time < 30 else '❌ MISSED'})")

if __name__ == "__main__":
    print("🎯 Choose test mode:")
    print("1. Full Integration Test (lesson + chatbot)")
    print("2. Quick Performance Test (generation only)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_lesson_system())
    elif choice == "2":
        asyncio.run(test_quick_performance())
    else:
        print("Invalid choice. Running full integration test...")
        asyncio.run(test_lesson_system())
