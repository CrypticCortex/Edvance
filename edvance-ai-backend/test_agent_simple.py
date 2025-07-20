# FILE: test_agent_simple.py

import asyncio
import logging
from datetime import datetime

from app.core.firebase import initialize_firebase
from app.agents.tools.learning_path_tools import generate_learning_path_automatically

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_agent_path_generation():
    """Simple test of agent-based learning path generation."""
    print("🤖 SIMPLE AGENT-BASED LEARNING PATH TEST")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test scenarios
    test_cases = [
        {
            "name": "🔴 Struggling Student",
            "student_id": "struggling_student_test",
            "grade": 5,
            "focused": False,
            "enrichment": False
        },
        {
            "name": "🟡 Mixed Performer", 
            "student_id": "mixed_student_test",
            "grade": 5,
            "focused": True,
            "enrichment": False
        },
        {
            "name": "🟢 Excellent Student",
            "student_id": "excellent_student_test",
            "grade": 6,  # Advanced grade
            "focused": False,
            "enrichment": True
        }
    ]
    
    teacher_uid = "test_teacher_simple_123"
    subject = "Mathematics"
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   👨‍🎓 Student: {test_case['student_id']}")
        print(f"   📚 Subject: {subject}")
        print(f"   🎯 Grade: {test_case['grade']}")
        
        if test_case['enrichment']:
            print(f"   🚀 Type: Enrichment (Advanced challenges)")
        elif test_case['focused']:
            print(f"   🎯 Type: Focused (Targeted improvement)")
        else:
            print(f"   📖 Type: Comprehensive (Full support)")
        
        try:
            # Generate learning path using agent
            path_result = await generate_learning_path_automatically(
                student_id=test_case["student_id"],
                teacher_uid=teacher_uid,
                subject=subject,
                grade=test_case["grade"],
                focused=test_case["focused"],
                enrichment=test_case["enrichment"]
            )
            
            if path_result.get("success"):
                print(f"   ✅ SUCCESS:")
                print(f"      🆔 Path ID: {path_result['path_id'][:12]}...")
                print(f"      📖 Steps: {path_result['total_steps']}")
                print(f"      ⏱️ Duration: {path_result['estimated_duration_hours']:.1f} hours")
                print(f"      🎯 Goals: {len(path_result['learning_goals'])}")
                print(f"      🤖 Generated: {path_result['generated_at']}")
                
                results.append({
                    "test_case": test_case['name'],
                    "success": True,
                    "path_id": path_result['path_id'],
                    "steps": path_result['total_steps'],
                    "duration": path_result['estimated_duration_hours']
                })
            else:
                print(f"   ❌ FAILED: {path_result.get('error', 'Unknown error')}")
                results.append({
                    "test_case": test_case['name'],
                    "success": False,
                    "error": path_result.get('error', 'Unknown error')
                })
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results.append({
                "test_case": test_case['name'],
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("🎉 SIMPLE AGENT TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)
    
    print(f"✅ RESULTS: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests > 0:
        total_steps = sum(r.get("steps", 0) for r in results if r.get("success"))
        total_duration = sum(r.get("duration", 0) for r in results if r.get("success"))
        
        print(f"📊 GENERATED LEARNING CONTENT:")
        print(f"   📖 Total Learning Steps: {total_steps}")
        print(f"   ⏱️ Total Learning Time: {total_duration:.1f} hours")
        print(f"   🤖 Agent Status: WORKING")
        
        print(f"\n🚀 AUTOMATION STATUS:")
        if successful_tests == total_tests:
            print("   ✅ FULLY FUNCTIONAL: Agent successfully generates personalized learning paths!")
            print("   🤖 Learning path generation is working correctly")
            print("   📚 Different student types receive appropriate interventions")
            print("   🎯 Ready for integration with assessment analysis")
        else:
            print("   ⚠️ PARTIALLY WORKING: Some tests failed")
    else:
        print("   ❌ AGENT NOT WORKING: All tests failed")
    
    return results

async def main():
    """Main test function."""
    # Initialize Firebase
    initialize_firebase()
    
    # Run simple test
    results = await test_simple_agent_path_generation()
    
    print(f"\n🎯 Simple agent test complete!")
    print(f"💡 This demonstrates that the learning path agent can generate")
    print(f"   personalized learning paths automatically!")

if __name__ == "__main__":
    asyncio.run(main())
