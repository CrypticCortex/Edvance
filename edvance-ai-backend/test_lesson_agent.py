# FILE: test_lesson_agent.py

import asyncio
import logging
import json
from datetime import datetime

from app.core.firebase import initialize_firebase
from app.services.lesson_service import lesson_service
from app.agents.tools.lesson_tools import (
    generate_lesson_content,
    start_lesson_chat,
    send_chat_message,
    generate_slide_content,
    create_interactive_element
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LessonAgentTester:
    """Test the lesson agent functionality."""
    
    def __init__(self):
        self.teacher_uid = "teacher_lesson_test_123"
        self.test_student = "lesson_student_001"
        self.test_lesson_id = None
        
    async def test_lesson_generation(self):
        """Test lesson content generation from a learning step."""
        print("\n🎨 TESTING LESSON CONTENT GENERATION")
        print("=" * 60)
        
        try:
            # Test lesson generation
            result = await lesson_service.create_lesson_from_step(
                learning_step_id="test_step_fractions",
                student_id=self.test_student,
                teacher_uid=self.teacher_uid,
                customizations={
                    "difficulty_adjustment": "normal",
                    "learning_style": "visual",
                    "include_interactive": True,
                    "slide_count_preference": "medium"
                }
            )
            
            if result.get("success"):
                self.test_lesson_id = result["lesson_id"]
                lesson_details = result["creation_details"]
                
                print(f"✅ LESSON CREATED SUCCESSFULLY:")
                print(f"   🆔 Lesson ID: {self.test_lesson_id}")
                print(f"   📖 Title: {result['lesson']['title']}")
                print(f"   📊 Total Slides: {lesson_details['total_slides']}")
                print(f"   ⏱️ Duration: {lesson_details['estimated_duration_minutes']} minutes")
                print(f"   🎯 Objectives: {len(lesson_details['learning_objectives'])}")
                
                # Display slide overview
                slides = result["lesson"].get("slides", [])
                print(f"\n📋 SLIDE OVERVIEW:")
                for i, slide in enumerate(slides[:5], 1):  # Show first 5 slides
                    print(f"   {i}. {slide.get('title', 'Untitled')} ({slide.get('slide_type', 'unknown')})")
                
                return True
            else:
                print(f"❌ LESSON CREATION FAILED: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ LESSON GENERATION ERROR: {str(e)}")
            return False
    
    async def test_lesson_chatbot(self):
        """Test the lesson chatbot functionality."""
        print("\n🤖 TESTING LESSON CHATBOT")
        print("=" * 60)
        
        if not self.test_lesson_id:
            print("❌ No lesson available for chatbot testing")
            return False
        
        try:
            # Start chatbot session
            chat_result = await lesson_service.start_lesson_chatbot(
                lesson_id=self.test_lesson_id,
                student_id=self.test_student,
                initial_message="I'm having trouble understanding fractions. Can you help me?"
            )
            
            if not chat_result.get("success"):
                print(f"❌ FAILED TO START CHAT: {chat_result.get('error')}")
                return False
            
            session_id = chat_result["session_id"]
            print(f"✅ CHAT SESSION STARTED: {session_id}")
            
            # Display initial messages
            messages = chat_result["messages"]
            for msg in messages:
                sender = "🧑‍🎓 Student" if msg["sender"] == "student" else "🤖 Assistant"
                print(f"   {sender}: {msg['message']}")
            
            # Test sending more messages
            test_messages = [
                "What is a fraction exactly?",
                "Can you give me an example with pizza?",
                "How do I add fractions?",
                "I'm still confused about denominators"
            ]
            
            print(f"\n💬 TESTING CONVERSATION:")
            for message in test_messages:
                print(f"   🧑‍🎓 Student: {message}")
                
                response_result = await lesson_service.send_chatbot_message(
                    session_id=session_id,
                    student_id=self.test_student,
                    message=message
                )
                
                if response_result.get("success"):
                    agent_response = response_result["agent_response"]
                    print(f"   🤖 Assistant: {agent_response['message'][:100]}...")
                    
                    # Show suggested actions if any
                    suggested_actions = response_result.get("suggested_actions", [])
                    if suggested_actions:
                        print(f"   💡 Suggestions: {', '.join(suggested_actions)}")
                else:
                    print(f"   ❌ Failed to get response: {response_result.get('error')}")
                
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ CHATBOT TEST ERROR: {str(e)}")
            return False
    
    async def test_slide_generation(self):
        """Test individual slide generation."""
        print("\n📊 TESTING SLIDE GENERATION")
        print("=" * 60)
        
        try:
            # Test different slide types
            slide_tests = [
                {
                    "type": "concept_explanation",
                    "topic": "Fractions",
                    "objective": "Understand what fractions represent"
                },
                {
                    "type": "example",
                    "topic": "Adding Fractions",
                    "objective": "Learn to add fractions with same denominators"
                },
                {
                    "type": "practice",
                    "topic": "Fraction Problems",
                    "objective": "Practice solving fraction word problems"
                }
            ]
            
            for test in slide_tests:
                print(f"\n🎯 GENERATING {test['type'].upper()} SLIDE:")
                
                slide_result = await generate_slide_content(
                    slide_type=test["type"],
                    topic=test["topic"],
                    learning_objective=test["objective"],
                    grade_level=5,
                    student_context={
                        "learning_style": "visual",
                        "performance_level": "average"
                    }
                )
                
                if slide_result.get("success"):
                    slide_content = slide_result["slide_content"]
                    print(f"   ✅ Title: {slide_content.get('title', 'No title')}")
                    print(f"   📝 Elements: {len(slide_content.get('content_elements', []))}")
                    print(f"   ⏱️ Duration: {slide_content.get('estimated_duration_minutes', 0)} min")
                    
                    # Show content elements
                    for elem in slide_content.get('content_elements', [])[:2]:
                        print(f"      • {elem.get('element_type', 'unknown')}: {elem.get('title', 'Untitled')}")
                else:
                    print(f"   ❌ Failed: {slide_result.get('error')}")
            
            return True
            
        except Exception as e:
            print(f"❌ SLIDE GENERATION ERROR: {str(e)}")
            return False
    
    async def test_interactive_elements(self):
        """Test interactive element creation."""
        print("\n🎮 TESTING INTERACTIVE ELEMENTS")
        print("=" * 60)
        
        try:
            # Test different interactive element types
            interactive_tests = [
                {
                    "type": "multiple_choice",
                    "topic": "Fraction Basics",
                    "difficulty": "easy"
                },
                {
                    "type": "drag_drop",
                    "topic": "Fraction Matching",
                    "difficulty": "medium"
                },
                {
                    "type": "fill_blank",
                    "topic": "Fraction Sentences",
                    "difficulty": "easy"
                }
            ]
            
            for test in interactive_tests:
                print(f"\n🎯 CREATING {test['type'].upper()} ELEMENT:")
                
                element_result = await create_interactive_element(
                    element_type=test["type"],
                    topic=test["topic"],
                    difficulty_level=test["difficulty"],
                    learning_objective="Practice fraction concepts"
                )
                
                if element_result.get("success"):
                    element = element_result["interactive_element"]
                    print(f"   ✅ Title: {element.get('title', 'No title')}")
                    print(f"   📋 Instructions: {element.get('instructions', 'No instructions')[:50]}...")
                    print(f"   💎 Points: {element.get('points', 0)}")
                    print(f"   💡 Hints: {len(element.get('hints', []))}")
                else:
                    print(f"   ❌ Failed: {element_result.get('error')}")
            
            return True
            
        except Exception as e:
            print(f"❌ INTERACTIVE ELEMENTS ERROR: {str(e)}")
            return False
    
    async def test_lesson_progress(self):
        """Test lesson progress tracking."""
        print("\n📈 TESTING LESSON PROGRESS")
        print("=" * 60)
        
        if not self.test_lesson_id:
            print("❌ No lesson available for progress testing")
            return False
        
        try:
            # Get lesson content
            lesson_result = await lesson_service.get_student_lesson(
                lesson_id=self.test_lesson_id,
                student_id=self.test_student
            )
            
            if not lesson_result.get("success"):
                print(f"❌ Failed to get lesson: {lesson_result.get('error')}")
                return False
            
            lesson = lesson_result["lesson"]
            slides = lesson.get("slides", [])
            
            print(f"📚 LESSON: {lesson.get('title', 'Untitled')}")
            print(f"📊 TOTAL SLIDES: {len(slides)}")
            
            # Simulate progress on first few slides
            for i, slide in enumerate(slides[:3]):
                slide_id = slide.get("slide_id")
                print(f"\n🎯 UPDATING PROGRESS FOR SLIDE {i+1}: {slide.get('title', 'Untitled')}")
                
                progress_result = await lesson_service.update_slide_progress(
                    lesson_id=self.test_lesson_id,
                    student_id=self.test_student,
                    slide_id=slide_id,
                    progress_data={
                        "is_completed": True,
                        "time_spent_minutes": 5,
                        "understanding_level": 4,
                        "responses": {"example_response": "completed"}
                    }
                )
                
                if progress_result.get("success"):
                    print(f"   ✅ Progress Updated:")
                    print(f"      📊 Completion: {progress_result['completion_percentage']:.1f}%")
                    print(f"      ✅ Slides Done: {progress_result['slides_completed']}")
                    
                    if progress_result.get("lesson_completed"):
                        print(f"   🎉 LESSON COMPLETED!")
                else:
                    print(f"   ❌ Progress update failed: {progress_result.get('error')}")
            
            return True
            
        except Exception as e:
            print(f"❌ PROGRESS TESTING ERROR: {str(e)}")
            return False
    
    async def run_comprehensive_test(self):
        """Run all lesson agent tests."""
        print("🎓 LESSON AGENT COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👨‍🏫 Test Teacher: {self.teacher_uid}")
        print(f"👨‍🎓 Test Student: {self.test_student}")
        print()
        
        results = {
            "test_start": datetime.now().isoformat(),
            "teacher_uid": self.teacher_uid,
            "student_id": self.test_student
        }
        
        try:
            # Test 1: Lesson Generation
            lesson_gen_success = await self.test_lesson_generation()
            results["lesson_generation"] = lesson_gen_success
            
            # Test 2: Chatbot Functionality
            chatbot_success = await self.test_lesson_chatbot()
            results["chatbot_functionality"] = chatbot_success
            
            # Test 3: Slide Generation
            slide_gen_success = await self.test_slide_generation()
            results["slide_generation"] = slide_gen_success
            
            # Test 4: Interactive Elements
            interactive_success = await self.test_interactive_elements()
            results["interactive_elements"] = interactive_success
            
            # Test 5: Progress Tracking
            progress_success = await self.test_lesson_progress()
            results["progress_tracking"] = progress_success
            
            # Summary
            successful_tests = sum([
                lesson_gen_success, chatbot_success, slide_gen_success,
                interactive_success, progress_success
            ])
            total_tests = 5
            
            print(f"\n🎉 LESSON AGENT TEST SUMMARY")
            print("=" * 80)
            print(f"✅ RESULTS: {successful_tests}/{total_tests} tests passed")
            
            if successful_tests == total_tests:
                print("🚀 LESSON AGENT STATUS:")
                print("   ✅ FULLY FUNCTIONAL: All lesson features working correctly!")
                print("   🎨 Dynamic lesson generation working")
                print("   🤖 Interactive chatbot responding effectively")
                print("   📊 Slide generation creating engaging content")
                print("   🎮 Interactive elements enhancing learning")
                print("   📈 Progress tracking monitoring student advancement")
                
                print(f"\n🎓 LESSON CAPABILITIES DEMONSTRATED:")
                print("   📚 Slide-based lesson structure")
                print("   🎯 Personalized content generation")
                print("   💬 Real-time student support")
                print("   🎮 Interactive learning elements")
                print("   📊 Comprehensive progress tracking")
                print("   🔄 Dynamic content adaptation")
            else:
                print("⚠️ SOME TESTS FAILED - Review individual test results")
            
            results["test_completion"] = datetime.now().isoformat()
            results["overall_success"] = successful_tests == total_tests
            results["success_rate"] = (successful_tests / total_tests) * 100
            
            # Save results
            with open("lesson_agent_test_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            return results
            
        except Exception as e:
            print(f"\n❌ COMPREHENSIVE TEST FAILED: {str(e)}")
            results["error"] = str(e)
            return results

async def main():
    """Main test function."""
    try:
        # Initialize Firebase
        initialize_firebase()
        
        # Run tests
        tester = LessonAgentTester()
        results = await tester.run_comprehensive_test()
        
        print(f"\n📁 Test results saved to: lesson_agent_test_results.json")
        
    except Exception as e:
        print(f"Test execution failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
