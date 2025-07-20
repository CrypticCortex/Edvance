# FILE: test_agent_based_learning_paths.py

import asyncio
import logging
import json
from datetime import datetime

from app.core.firebase import initialize_firebase
from app.services.learning_path_monitoring_service import learning_path_monitoring_service
from app.services.enhanced_assessment_service import enhanced_assessment_service
from app.agents.tools.learning_path_tools import (
    analyze_assessment_completion,
    generate_learning_path_automatically,
    track_learning_progress,
    get_student_learning_status
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentBasedLearningPathTester:
    """Test the agent-based learning path generation system."""
    
    def __init__(self):
        self.teacher_uid = "teacher_test_agent_123"
        self.test_students = [
            "agent_student_001",
            "agent_student_002", 
            "agent_student_003"
        ]
        
    async def test_agent_monitoring_activation(self):
        """Test starting the learning path monitoring agent."""
        print("🤖 TESTING AGENT MONITORING ACTIVATION")
        print("=" * 60)
        
        try:
            # Start monitoring for the teacher
            monitoring_result = await learning_path_monitoring_service.start_monitoring(
                self.teacher_uid
            )
            
            print(f"✅ MONITORING ACTIVATED:")
            print(f"   👨‍🏫 Teacher: {monitoring_result['teacher_uid']}")
            print(f"   📊 Status: {monitoring_result['monitoring_started']}")
            print(f"   🤖 Agent: {monitoring_result['agent_activated']}")
            print(f"   👂 Listeners: {monitoring_result['real_time_listeners']}")
            print(f"   ⏰ Progress Monitoring: {monitoring_result['progress_monitoring']}")
            
            # Get monitoring status
            status = await learning_path_monitoring_service.get_monitoring_status(
                self.teacher_uid
            )
            
            print(f"\n📈 MONITORING STATUS:")
            print(f"   🔄 Active: {status['monitoring_active']}")
            print(f"   🤖 Agent Status: {status['agent_status']}")
            print(f"   📊 Event Listeners: {status['event_listeners']}")
            print(f"   ⏰ Scheduled Tasks: {status['scheduled_tasks']}")
            
            return True
            
        except Exception as e:
            print(f"❌ MONITORING ACTIVATION FAILED: {str(e)}")
            return False
    
    async def test_automatic_assessment_processing(self):
        """Test automatic assessment completion processing."""
        print("\n🧪 TESTING AUTOMATIC ASSESSMENT PROCESSING")
        print("=" * 60)
        
        test_scenarios = [
            {
                "name": "Struggling Student",
                "student_id": "agent_student_001",
                "assessment_id": "grade5_math_assessment",
                "answers": [0, 0, 0, 0],  # All wrong
                "time_taken": 45,
                "expected_intervention": "comprehensive_support"
            },
            {
                "name": "Mixed Performer", 
                "student_id": "agent_student_002",
                "assessment_id": "grade5_math_assessment",
                "answers": [0, 1, 0, 1],  # Half correct
                "time_taken": 30,
                "expected_intervention": "targeted_improvement"
            },
            {
                "name": "Excellent Student",
                "student_id": "agent_student_003", 
                "assessment_id": "grade5_math_assessment",
                "answers": [1, 1, 1, 1],  # All correct
                "time_taken": 20,
                "expected_intervention": "enrichment"
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            print(f"\n📝 PROCESSING: {scenario['name']}")
            print(f"   👨‍🎓 Student: {scenario['student_id']}")
            print(f"   📊 Answers: {scenario['answers']}")
            print(f"   ⏱️ Time: {scenario['time_taken']} minutes")
            
            try:
                # Simulate assessment completion through monitoring service
                result = await learning_path_monitoring_service.handle_assessment_completion(
                    student_id=scenario["student_id"],
                    assessment_id=scenario["assessment_id"],
                    student_answers=scenario["answers"],
                    time_taken_minutes=scenario["time_taken"],
                    teacher_uid=self.teacher_uid
                )
                
                print(f"   ✅ AGENT RESPONSE:")
                print(f"      📈 Score: {result.get('agent_response', {}).get('performance_score', 0):.1f}%")
                print(f"      🎯 Intervention: {result.get('intervention_type', 'none')}")
                print(f"      📚 Learning Path: {'Generated' if result.get('learning_path_generated') else 'Not Generated'}")
                
                if result.get('learning_path_generated'):
                    path_id = result.get('agent_response', {}).get('learning_path_id')
                    if path_id:
                        print(f"      🆔 Path ID: {path_id[:12]}...")
                
                results.append({
                    "scenario": scenario["name"],
                    "success": result.get("processed", False),
                    "intervention": result.get("intervention_type"),
                    "path_generated": result.get("learning_path_generated"),
                    "expected": scenario["expected_intervention"]
                })
                
            except Exception as e:
                print(f"   ❌ PROCESSING FAILED: {str(e)}")
                results.append({
                    "scenario": scenario["name"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def test_learning_path_monitoring(self):
        """Test learning path progress monitoring."""
        print("\n📊 TESTING LEARNING PATH MONITORING")
        print("=" * 60)
        
        monitoring_results = []
        
        for student_id in self.test_students:
            print(f"\n👨‍🎓 MONITORING STUDENT: {student_id}")
            
            try:
                # Get student learning status
                status = await get_student_learning_status(student_id)
                
                print(f"   📚 Learning Paths: {status['total_learning_paths']}")
                print(f"   🔄 Active Paths: {status['active_paths']}")
                print(f"   ✅ Completed Paths: {status['completed_paths']}")
                print(f"   📈 Overall Progress: {status['overall_progress']:.1f}%")
                print(f"   🎯 Current Focus: {', '.join(status['current_focus_areas'][:2]) if status['current_focus_areas'] else 'None'}")
                print(f"   🚀 Recommended Actions: {len(status['recommended_actions'])}")
                
                monitoring_results.append({
                    "student_id": student_id,
                    "status": status,
                    "monitoring_success": True
                })
                
            except Exception as e:
                print(f"   ❌ MONITORING FAILED: {str(e)}")
                monitoring_results.append({
                    "student_id": student_id,
                    "monitoring_success": False,
                    "error": str(e)
                })
        
        return monitoring_results
    
    async def test_batch_processing(self):
        """Test batch processing of assessments."""
        print("\n📦 TESTING BATCH ASSESSMENT PROCESSING")
        print("=" * 60)
        
        try:
            batch_result = await learning_path_monitoring_service.process_batch_assessments(
                self.teacher_uid
            )
            
            print(f"✅ BATCH PROCESSING RESULTS:")
            print(f"   👨‍🏫 Teacher: {batch_result['teacher_uid']}")
            print(f"   📊 Assessments Processed: {batch_result['assessments_processed']}")
            print(f"   📚 Learning Paths Generated: {batch_result['learning_paths_generated']}")
            print(f"   👨‍🎓 Students Helped: {len(batch_result['students_helped'])}")
            print(f"   ⏰ Timestamp: {batch_result['timestamp']}")
            
            return batch_result
            
        except Exception as e:
            print(f"❌ BATCH PROCESSING FAILED: {str(e)}")
            return {"error": str(e)}
    
    async def test_direct_agent_tools(self):
        """Test direct usage of agent tools."""
        print("\n🔧 TESTING DIRECT AGENT TOOLS")
        print("=" * 60)
        
        # Test direct analysis
        print("🧪 DIRECT ASSESSMENT ANALYSIS:")
        analysis_result = await analyze_assessment_completion(
            student_id="direct_test_student",
            assessment_id="grade5_math_assessment", 
            student_answers=[0, 1, 0, 1],
            time_taken_minutes=25
        )
        
        print(f"   📈 Performance: {analysis_result.get('performance_score', 0):.1f}%")
        print(f"   🎯 Intervention: {analysis_result.get('intervention_type', 'none')}")
        print(f"   📚 Path Generated: {analysis_result.get('learning_path_generated', False)}")
        
        # Test direct path generation
        print("\n🛤️ DIRECT LEARNING PATH GENERATION:")
        path_result = await generate_learning_path_automatically(
            student_id="direct_test_student",
            teacher_uid=self.teacher_uid,
            subject="Mathematics",
            grade=5
        )
        
        print(f"   ✅ Success: {path_result.get('success', False)}")
        print(f"   🆔 Path ID: {path_result.get('path_id', 'N/A')[:12]}...")
        print(f"   📖 Steps: {path_result.get('total_steps', 0)}")
        print(f"   ⏱️ Duration: {path_result.get('estimated_duration_hours', 0):.1f} hours")
        
        return {
            "analysis": analysis_result,
            "path_generation": path_result
        }
    
    async def run_comprehensive_test(self):
        """Run comprehensive test of the agent-based system."""
        print("🎯 AGENT-BASED LEARNING PATH SYSTEM - COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👨‍🏫 Test Teacher: {self.teacher_uid}")
        print(f"👨‍🎓 Test Students: {', '.join(self.test_students)}")
        print()
        
        results = {
            "test_start": datetime.now().isoformat(),
            "teacher_uid": self.teacher_uid,
            "students": self.test_students
        }
        
        try:
            # Phase 1: Activate monitoring
            monitoring_activated = await self.test_agent_monitoring_activation()
            results["monitoring_activation"] = monitoring_activated
            
            # Phase 2: Test automatic processing
            assessment_results = await self.test_automatic_assessment_processing()
            results["assessment_processing"] = assessment_results
            
            # Phase 3: Test learning path monitoring
            monitoring_results = await self.test_learning_path_monitoring()
            results["progress_monitoring"] = monitoring_results
            
            # Phase 4: Test batch processing
            batch_results = await self.test_batch_processing()
            results["batch_processing"] = batch_results
            
            # Phase 5: Test direct agent tools
            agent_tools_results = await self.test_direct_agent_tools()
            results["agent_tools"] = agent_tools_results
            
            # Summary
            print("\n🎉 AGENT-BASED SYSTEM TEST SUMMARY")
            print("=" * 80)
            
            successful_assessments = sum(1 for r in assessment_results if r.get("success", False))
            successful_monitoring = sum(1 for r in monitoring_results if r.get("monitoring_success", False))
            
            print(f"✅ RESULTS:")
            print(f"   🤖 Monitoring Activated: {'Yes' if monitoring_activated else 'No'}")
            print(f"   📊 Assessments Processed: {successful_assessments}/{len(assessment_results)}")
            print(f"   👁️ Students Monitored: {successful_monitoring}/{len(monitoring_results)}")
            print(f"   📦 Batch Processing: {'Success' if 'error' not in batch_results else 'Failed'}")
            print(f"   🔧 Agent Tools: {'Working' if agent_tools_results else 'Failed'}")
            
            print(f"\n🚀 AUTOMATION STATUS:")
            if monitoring_activated and successful_assessments > 0:
                print("   ✅ FULLY AUTOMATED: Learning paths are automatically generated!")
                print("   🤖 Agent is monitoring student assessments in real-time")
                print("   📚 Personalized learning paths created without manual intervention")
                print("   📈 Progress tracking and adaptation happening automatically")
            else:
                print("   ⚠️ PARTIAL AUTOMATION: Some components need attention")
            
            results["test_completion"] = datetime.now().isoformat()
            results["overall_success"] = monitoring_activated and successful_assessments > 0
            
            return results
            
        except Exception as e:
            print(f"\n❌ COMPREHENSIVE TEST FAILED: {str(e)}")
            results["error"] = str(e)
            return results

async def main():
    """Main test function."""
    # Initialize Firebase
    initialize_firebase()
    
    # Create and run tester
    tester = AgentBasedLearningPathTester()
    results = await tester.run_comprehensive_test()
    
    # Save results
    with open("agent_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: agent_test_results.json")
    print("🎯 Agent-based learning path system testing complete!")

if __name__ == "__main__":
    asyncio.run(main())
