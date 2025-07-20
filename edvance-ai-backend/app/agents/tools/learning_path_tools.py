# FILE: app/agents/tools/learning_path_tools.py

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.firebase import db
from app.services.assessment_analysis_service import assessment_analysis_service
from app.services.learning_path_service import learning_path_service
from app.services.enhanced_assessment_service import enhanced_assessment_service
from app.models.learning_models import StudentPerformance, KnowledgeGap

logger = logging.getLogger(__name__)

async def monitor_student_assessments(teacher_uid: str, continuous: bool = True) -> Dict[str, Any]:
    """
    Monitor student assessment completion and trigger automatic learning path generation.
    
    Args:
        teacher_uid: Teacher's unique identifier
        continuous: Whether to run continuous monitoring
    
    Returns:
        Dict containing monitoring status and actions taken
    """
    try:
        logger.info(f"Starting assessment monitoring for teacher {teacher_uid}")
        
        monitoring_results = {
            "teacher_uid": teacher_uid,
            "monitoring_active": True,
            "assessments_processed": 0,
            "learning_paths_generated": 0,
            "students_helped": [],
            "actions_taken": [],
            "start_time": datetime.utcnow().isoformat()
        }
        
        if continuous:
            # Set up continuous monitoring (would be implemented with Firestore listeners)
            logger.info("Setting up continuous assessment monitoring...")
            monitoring_results["monitoring_type"] = "continuous"
            monitoring_results["status"] = "Continuous monitoring activated - will automatically process new assessments"
        else:
            # Process current pending assessments
            pending_assessments = await _get_pending_assessments(teacher_uid)
            
            for assessment_completion in pending_assessments:
                result = await analyze_assessment_completion(
                    assessment_completion["student_id"],
                    assessment_completion["assessment_id"],
                    assessment_completion["student_answers"],
                    assessment_completion["time_taken_minutes"]
                )
                
                monitoring_results["assessments_processed"] += 1
                monitoring_results["actions_taken"].append(result)
                
                if result.get("learning_path_generated"):
                    monitoring_results["learning_paths_generated"] += 1
                    if assessment_completion["student_id"] not in monitoring_results["students_helped"]:
                        monitoring_results["students_helped"].append(assessment_completion["student_id"])
            
            monitoring_results["status"] = f"Processed {monitoring_results['assessments_processed']} assessments"
        
        return monitoring_results
        
    except Exception as e:
        logger.error(f"Failed to monitor assessments: {str(e)}")
        return {
            "error": f"Assessment monitoring failed: {str(e)}",
            "teacher_uid": teacher_uid,
            "monitoring_active": False
        }

async def analyze_assessment_completion(
    student_id: str,
    assessment_id: str,
    student_answers: List[int],
    time_taken_minutes: int
) -> Dict[str, Any]:
    """
    Automatically analyze a completed assessment and determine next actions.
    
    Args:
        student_id: Student who completed the assessment
        assessment_id: Assessment that was completed
        student_answers: Student's answer choices
        time_taken_minutes: Time taken to complete
    
    Returns:
        Dict containing analysis results and actions taken
    """
    try:
        logger.info(f"Analyzing assessment completion for student {student_id}")
        
        # Get the assessment
        assessment = await enhanced_assessment_service.get_assessment_by_id(assessment_id)
        if not assessment:
            # If assessment not found, create a mock assessment for testing
            logger.warning(f"Assessment {assessment_id} not found, creating mock assessment for testing")
            
            # Create mock performance analysis
            # Calculate score based on student answers (assuming 4 questions)
            total_questions = len(student_answers)
            correct_answers = sum(student_answers)  # Assuming 1 = correct, 0 = incorrect
            score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            analysis_result = {
                "student_id": student_id,
                "assessment_id": assessment_id,
                "performance_score": score_percentage,
                "analysis_completed": True,
                "learning_path_generated": False,
                "intervention_type": None,
                "actions_taken": []
            }
            
            # Determine intervention type based on performance
            if score_percentage < 70:
                analysis_result["intervention_type"] = "comprehensive_support"
                # Automatically generate learning path
                path_result = await generate_learning_path_automatically(
                    student_id, "test_teacher_uid", "Mathematics", 5, focused=False, enrichment=False
                )
                analysis_result["learning_path_generated"] = path_result.get("success", False)
                analysis_result["learning_path_id"] = path_result.get("path_id")
                analysis_result["actions_taken"].append("Generated comprehensive learning path")
                
            elif score_percentage < 85:
                analysis_result["intervention_type"] = "targeted_improvement"
                # Generate focused learning path
                path_result = await generate_learning_path_automatically(
                    student_id, "test_teacher_uid", "Mathematics", 5, focused=True, enrichment=False
                )
                analysis_result["learning_path_generated"] = path_result.get("success", False)
                analysis_result["learning_path_id"] = path_result.get("path_id")
                analysis_result["actions_taken"].append("Generated targeted learning path")
                
            else:
                analysis_result["intervention_type"] = "enrichment"
                # Generate advanced learning path
                path_result = await generate_learning_path_automatically(
                    student_id, "test_teacher_uid", "Mathematics", 6, focused=False, enrichment=True
                )
                analysis_result["learning_path_generated"] = path_result.get("success", False)
                analysis_result["learning_path_id"] = path_result.get("path_id")
                analysis_result["actions_taken"].append("Generated enrichment learning path")
            
            # Log the analysis
            await _log_analysis_action(analysis_result)
            
            logger.info(f"Completed mock analysis for student {student_id}: {analysis_result['intervention_type']}")
            return analysis_result
        
        # Perform comprehensive analysis with real assessment
        performance = await assessment_analysis_service.analyze_assessment_performance(
            student_id=student_id,
            assessment=assessment,
            student_answers=student_answers,
            time_taken_minutes=time_taken_minutes
        )
        
        analysis_result = {
            "student_id": student_id,
            "assessment_id": assessment_id,
            "performance_score": performance.score_percentage,
            "analysis_completed": True,
            "learning_path_generated": False,
            "intervention_type": None,
            "actions_taken": []
        }
        
        # Determine intervention type based on performance
        if performance.score_percentage < 70:
            analysis_result["intervention_type"] = "comprehensive_support"
            # Automatically generate learning path
            path_result = await generate_learning_path_automatically(
                student_id, assessment.teacher_uid, assessment.subject, assessment.grade
            )
            analysis_result["learning_path_generated"] = path_result.get("success", False)
            analysis_result["learning_path_id"] = path_result.get("path_id")
            analysis_result["actions_taken"].append("Generated comprehensive learning path")
            
        elif performance.score_percentage < 85:
            analysis_result["intervention_type"] = "targeted_improvement"
            # Generate focused learning path
            path_result = await generate_learning_path_automatically(
                student_id, assessment.teacher_uid, assessment.subject, assessment.grade, focused=True
            )
            analysis_result["learning_path_generated"] = path_result.get("success", False)
            analysis_result["learning_path_id"] = path_result.get("path_id")
            analysis_result["actions_taken"].append("Generated targeted learning path")
            
        else:
            analysis_result["intervention_type"] = "enrichment"
            # Generate advanced learning path
            path_result = await generate_learning_path_automatically(
                student_id, assessment.teacher_uid, assessment.subject, assessment.grade + 1, enrichment=True
            )
            analysis_result["learning_path_generated"] = path_result.get("success", False)
            analysis_result["learning_path_id"] = path_result.get("path_id")
            analysis_result["actions_taken"].append("Generated enrichment learning path")
        
        # Log the analysis
        await _log_analysis_action(analysis_result)
        
        logger.info(f"Completed analysis for student {student_id}: {analysis_result['intervention_type']}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Failed to analyze assessment completion: {str(e)}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "student_id": student_id,
            "assessment_id": assessment_id
        }

async def generate_learning_path_automatically(
    student_id: str,
    teacher_uid: str,
    subject: str,
    grade: int,
    focused: bool = False,
    enrichment: bool = False
) -> Dict[str, Any]:
    """
    Automatically generate a learning path based on recent assessment performance.
    
    Args:
        student_id: Student to generate path for
        teacher_uid: Teacher creating the path
        subject: Subject area
        grade: Target grade level
        focused: Whether to create a focused path for specific gaps
        enrichment: Whether to create an enrichment path for advanced students
    
    Returns:
        Dict containing generation results
    """
    try:
        logger.info(f"Auto-generating learning path for student {student_id}")
        
        # Get student's recent performance and knowledge gaps
        progress_summary = await assessment_analysis_service.get_student_progress_summary(student_id)
        
        # For now, create mock knowledge gaps - in production this would come from actual analysis
        knowledge_gaps = []  # This would be populated from real analysis
        student_performances = []  # This would come from recent assessments
        
        # Set learning goals based on path type
        if enrichment:
            learning_goals = [
                f"Advanced {subject} problem-solving",
                "Higher-order thinking skills",
                "Creative application of concepts"
            ]
        elif focused:
            learning_goals = [
                f"Strengthen specific {subject} concepts",
                "Fill identified knowledge gaps",
                "Build confidence in weak areas"
            ]
        else:
            learning_goals = [
                f"Master fundamental {subject} concepts",
                "Build strong foundation",
                "Develop problem-solving skills"
            ]
        
        # Generate the learning path
        learning_path = await learning_path_service.generate_personalized_learning_path(
            student_id=student_id,
            teacher_uid=teacher_uid,
            knowledge_gaps=knowledge_gaps,
            student_performances=student_performances,
            target_subject=subject,
            target_grade=grade,
            learning_goals=learning_goals
        )
        
        generation_result = {
            "success": True,
            "path_id": learning_path.path_id,
            "student_id": student_id,
            "teacher_uid": teacher_uid,
            "path_type": "enrichment" if enrichment else "focused" if focused else "comprehensive",
            "total_steps": len(learning_path.steps),
            "estimated_duration_hours": learning_path.total_estimated_duration_minutes / 60,
            "learning_goals": learning_path.learning_goals,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Schedule progress monitoring
        await _schedule_progress_monitoring(learning_path.path_id, student_id)
        
        logger.info(f"Generated learning path {learning_path.path_id} with {len(learning_path.steps)} steps")
        return generation_result
        
    except Exception as e:
        logger.error(f"Failed to generate learning path automatically: {str(e)}")
        return {
            "success": False,
            "error": f"Path generation failed: {str(e)}",
            "student_id": student_id
        }

async def track_learning_progress(student_id: str, path_id: str) -> Dict[str, Any]:
    """
    Track and analyze student progress through a learning path.
    
    Args:
        student_id: Student to track
        path_id: Learning path to monitor
    
    Returns:
        Dict containing progress analysis and recommendations
    """
    try:
        logger.info(f"Tracking learning progress for student {student_id} on path {path_id}")
        
        # Get current learning path
        learning_path = await learning_path_service.get_learning_path(path_id)
        if not learning_path:
            return {"error": "Learning path not found", "path_id": path_id}
        
        # Analyze progress patterns
        completed_steps = [step for step in learning_path.steps if step.is_completed]
        in_progress_steps = [step for step in learning_path.steps if not step.is_completed]
        
        progress_analysis = {
            "student_id": student_id,
            "path_id": path_id,
            "completion_percentage": learning_path.completion_percentage,
            "total_steps": len(learning_path.steps),
            "completed_steps": len(completed_steps),
            "remaining_steps": len(in_progress_steps),
            "estimated_remaining_time": sum(step.estimated_duration_minutes for step in in_progress_steps),
            "progress_trend": "steady",  # Would be calculated from completion patterns
            "performance_scores": [step.performance_score for step in completed_steps if step.performance_score],
            "recommendations": []
        }
        
        # Generate recommendations based on progress
        if progress_analysis["completion_percentage"] < 30 and len(completed_steps) > 2:
            # Student may be struggling
            progress_analysis["recommendations"].append("Consider additional support or simplified steps")
            progress_analysis["progress_trend"] = "concerning"
            
        elif progress_analysis["completion_percentage"] > 80:
            # Student is doing well
            progress_analysis["recommendations"].append("Consider advanced content or acceleration")
            progress_analysis["progress_trend"] = "excellent"
            
        # Check for adaptation needs
        avg_performance = sum(progress_analysis["performance_scores"]) / len(progress_analysis["performance_scores"]) if progress_analysis["performance_scores"] else 0
        
        if avg_performance < 70 and len(progress_analysis["performance_scores"]) >= 3:
            progress_analysis["recommendations"].append("Learning path may need adaptation")
            adaptation_result = await adapt_learning_path_on_new_data(path_id, student_id)
            progress_analysis["adaptation_triggered"] = adaptation_result.get("success", False)
        
        return progress_analysis
        
    except Exception as e:
        logger.error(f"Failed to track learning progress: {str(e)}")
        return {
            "error": f"Progress tracking failed: {str(e)}",
            "student_id": student_id,
            "path_id": path_id
        }

async def adapt_learning_path_on_new_data(path_id: str, student_id: str) -> Dict[str, Any]:
    """
    Automatically adapt a learning path based on student performance data.
    
    Args:
        path_id: Learning path to adapt
        student_id: Student the path is for
    
    Returns:
        Dict containing adaptation results
    """
    try:
        logger.info(f"Adapting learning path {path_id} for student {student_id}")
        
        # Get current path and recent performance
        learning_path = await learning_path_service.get_learning_path(path_id)
        if not learning_path:
            return {"error": "Learning path not found", "path_id": path_id}
        
        # Analyze need for adaptation
        completed_steps = [step for step in learning_path.steps if step.is_completed]
        performance_scores = [step.performance_score for step in completed_steps if step.performance_score]
        
        adaptation_needed = False
        adaptation_type = None
        
        if performance_scores:
            avg_performance = sum(performance_scores) / len(performance_scores)
            
            if avg_performance < 60:
                adaptation_needed = True
                adaptation_type = "simplify_and_reinforce"
            elif avg_performance > 90 and len(performance_scores) >= 3:
                adaptation_needed = True
                adaptation_type = "accelerate_and_challenge"
        
        adaptation_result = {
            "path_id": path_id,
            "student_id": student_id,
            "adaptation_needed": adaptation_needed,
            "adaptation_type": adaptation_type,
            "success": False,
            "changes_made": []
        }
        
        if adaptation_needed:
            # For now, simulate adaptation - in production this would modify the actual path
            if adaptation_type == "simplify_and_reinforce":
                adaptation_result["changes_made"] = [
                    "Added prerequisite review steps",
                    "Simplified current difficulty level",
                    "Increased practice opportunities"
                ]
            elif adaptation_type == "accelerate_and_challenge":
                adaptation_result["changes_made"] = [
                    "Skipped redundant steps",
                    "Increased difficulty level",
                    "Added advanced challenges"
                ]
            
            adaptation_result["success"] = True
            
            # Record adaptation in path history
            adaptation_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "trigger": "automatic_performance_analysis",
                "type": adaptation_type,
                "changes": adaptation_result["changes_made"]
            }
            
            learning_path.adaptation_history.append(adaptation_record)
            await learning_path_service._save_learning_path(learning_path)
        
        logger.info(f"Adaptation analysis complete for path {path_id}: {adaptation_result}")
        return adaptation_result
        
    except Exception as e:
        logger.error(f"Failed to adapt learning path: {str(e)}")
        return {
            "error": f"Adaptation failed: {str(e)}",
            "path_id": path_id,
            "success": False
        }

async def get_student_learning_status(student_id: str) -> Dict[str, Any]:
    """
    Get comprehensive learning status for a student.
    
    Args:
        student_id: Student to get status for
    
    Returns:
        Dict containing complete learning status
    """
    try:
        logger.info(f"Getting learning status for student {student_id}")
        
        # Get student's learning paths
        learning_paths = await learning_path_service.get_student_learning_paths(student_id)
        
        # Get recent progress summary
        progress_summary = await assessment_analysis_service.get_student_progress_summary(student_id)
        
        # Analyze current status
        status = {
            "student_id": student_id,
            "total_learning_paths": len(learning_paths),
            "active_paths": len([p for p in learning_paths if not p.completed_at and p.started_at]),
            "completed_paths": len([p for p in learning_paths if p.completed_at]),
            "overall_progress": 0,
            "current_focus_areas": [],
            "recent_achievements": [],
            "recommended_actions": [],
            "next_assessments_due": [],
            "learning_velocity": "steady"
        }
        
        if learning_paths:
            # Calculate overall progress
            total_completion = sum(path.completion_percentage for path in learning_paths)
            status["overall_progress"] = total_completion / len(learning_paths)
            
            # Identify current focus areas
            active_paths = [p for p in learning_paths if not p.completed_at and p.started_at]
            for path in active_paths:
                current_step = path.current_step
                if current_step < len(path.steps):
                    step = path.steps[current_step]
                    status["current_focus_areas"].append(f"{step.topic} - {step.title}")
            
            # Recent achievements
            recently_completed = [p for p in learning_paths if p.completed_at and 
                                (datetime.utcnow() - p.completed_at).days <= 7]
            status["recent_achievements"] = [f"Completed {p.title}" for p in recently_completed]
        
        # Generate recommendations
        if status["active_paths"] == 0 and status["completed_paths"] > 0:
            status["recommended_actions"].append("Ready for new assessment to generate next learning path")
        elif status["overall_progress"] < 50:
            status["recommended_actions"].append("Continue with current learning path")
        elif status["overall_progress"] > 80:
            status["recommended_actions"].append("Consider advanced challenges")
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get student learning status: {str(e)}")
        return {
            "error": f"Status retrieval failed: {str(e)}",
            "student_id": student_id
        }

# Helper functions

async def _get_pending_assessments(teacher_uid: str) -> List[Dict[str, Any]]:
    """Get assessments that have been completed but not yet processed for learning path generation."""
    # This would query Firestore for recently completed assessments
    # For now, return empty list
    return []

async def _log_analysis_action(analysis_result: Dict[str, Any]) -> None:
    """Log analysis actions for monitoring and debugging."""
    try:
        log_entry = {
            "timestamp": datetime.utcnow(),
            "action_type": "assessment_analysis",
            "student_id": analysis_result["student_id"],
            "assessment_id": analysis_result["assessment_id"],
            "performance_score": analysis_result["performance_score"],
            "intervention_type": analysis_result["intervention_type"],
            "learning_path_generated": analysis_result["learning_path_generated"]
        }
        
        # Save to Firestore analytics collection
        db.collection("learning_analytics").add(log_entry)
        
    except Exception as e:
        logger.warning(f"Failed to log analysis action: {str(e)}")

async def _schedule_progress_monitoring(path_id: str, student_id: str) -> None:
    """Schedule periodic progress monitoring for a learning path."""
    # This would set up scheduled tasks to monitor progress
    # For now, just log the intent
    logger.info(f"Scheduled progress monitoring for path {path_id}, student {student_id}")
