# FILE: app/api/v1/personalized_learning.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List, Optional
import logging

from app.models.learning_models import (
    StudentPerformance, KnowledgeGap, LearningPath, 
    LearningRecommendation, LearningStep
)
from app.models.student import Assessment
from app.core.auth import get_current_user
from app.services.assessment_analysis_service import assessment_analysis_service
from app.services.learning_path_service import learning_path_service
from app.services.enhanced_assessment_service import enhanced_assessment_service
from app.services.learning_path_monitoring_service import learning_path_monitoring_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ====================================================================
# LEARNING PATH AGENT MONITORING ENDPOINTS
# ====================================================================

@router.post("/start-monitoring", response_model=Dict[str, Any])
async def start_learning_path_monitoring(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start automated learning path monitoring for the teacher's students.
    Once activated, the learning path agent will automatically:
    1. Monitor assessment completions
    2. Analyze student performance  
    3. Generate personalized learning paths
    4. Adapt paths based on progress
    """
    teacher_uid = current_user["uid"]
    
    try:
        monitoring_result = await learning_path_monitoring_service.start_monitoring(teacher_uid)
        
        return {
            "teacher_uid": teacher_uid,
            "monitoring_activated": monitoring_result.get("monitoring_started", False),
            "agent_status": "active",
            "automation_features": [
                "Assessment completion detection",
                "Automatic performance analysis", 
                "Personalized learning path generation",
                "Progress monitoring and adaptation",
                "Real-time intervention recommendations"
            ],
            "monitoring_result": monitoring_result,
            "message": "🤖 Learning Path Agent is now monitoring your students! Assessments will automatically trigger personalized learning paths."
        }
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Monitoring startup failed: {str(e)}"
        )

@router.get("/monitoring-status", response_model=Dict[str, Any])
async def get_monitoring_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current learning path monitoring status for the teacher."""
    teacher_uid = current_user["uid"]
    
    try:
        status = await learning_path_monitoring_service.get_monitoring_status(teacher_uid)
        
        return {
            "teacher_uid": teacher_uid,
            "monitoring_status": status,
            "agent_active": status.get("monitoring_active", False),
            "automation_enabled": True,
            "last_updated": status.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Status retrieval failed: {str(e)}"
        )

@router.post("/process-batch-assessments", response_model=Dict[str, Any])
async def process_batch_assessments(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Process all pending assessments and generate learning paths in batch.
    Useful for catching up on assessments completed before monitoring was active.
    """
    teacher_uid = current_user["uid"]
    
    try:
        batch_result = await learning_path_monitoring_service.process_batch_assessments(teacher_uid)
        
        return {
            "teacher_uid": teacher_uid,
            "batch_processing": batch_result,
            "assessments_processed": batch_result.get("assessments_processed", 0),
            "learning_paths_generated": batch_result.get("learning_paths_generated", 0),
            "students_helped": batch_result.get("students_helped", []),
            "message": f"🚀 Processed {batch_result.get('assessments_processed', 0)} assessments and generated {batch_result.get('learning_paths_generated', 0)} learning paths!"
        }
        
    except Exception as e:
        logger.error(f"Failed to process batch assessments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )

# ====================================================================
# ASSESSMENT ANALYSIS ENDPOINTS
# ====================================================================

@router.post("/analyze-assessment", response_model=Dict[str, Any])
async def analyze_student_assessment(
    assessment_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Analyze a student's assessment performance and identify learning needs.
    
    Expected format:
    {
        "student_id": "student_id",
        "assessment_id": "assessment_id", 
        "student_answers": [0, 1, 2, 0, 3],  # List of selected answer indices
        "time_taken_minutes": 25
    }
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Extract data
        student_id = assessment_data["student_id"]
        assessment_id = assessment_data["assessment_id"]
        student_answers = assessment_data["student_answers"]
        time_taken = assessment_data["time_taken_minutes"]
        
        # Get the assessment
        assessment = await enhanced_assessment_service.get_assessment_by_id(assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        # Verify teacher owns this assessment
        if assessment.teacher_uid != teacher_uid:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Not your assessment"
            )
        
        # Analyze performance
        performance = await assessment_analysis_service.analyze_assessment_performance(
            student_id=student_id,
            assessment=assessment,
            student_answers=student_answers,
            time_taken_minutes=time_taken
        )
        
        # 🤖 AUTOMATICALLY TRIGGER LEARNING PATH AGENT
        # This is where the magic happens - no manual intervention needed!
        agent_response = await learning_path_monitoring_service.handle_assessment_completion(
            student_id=student_id,
            assessment_id=assessment_id,
            student_answers=student_answers,
            time_taken_minutes=time_taken,
            teacher_uid=teacher_uid
        )
        
        logger.info(f"Analyzed assessment {assessment_id} for student {student_id}")
        
        return {
            "performance_id": performance.performance_id,
            "student_id": student_id,
            "assessment_id": assessment_id,
            "overall_score": performance.score_percentage,
            "time_taken": performance.time_taken_minutes,
            "topic_scores": performance.topic_scores,
            "difficulty_scores": performance.difficulty_scores,
            "strengths": performance.strengths,
            "weaknesses": performance.weaknesses,
            "recommended_focus_areas": performance.recommended_focus_areas,
            "analysis_completed": True,
            
            # 🚀 AGENT-POWERED AUTOMATION RESULTS
            "agent_intervention": {
                "triggered": True,
                "learning_path_generated": agent_response.get("learning_path_generated", False),
                "intervention_type": agent_response.get("intervention_type"),
                "agent_response": agent_response.get("agent_response", {}),
                "automated_action": "Learning path agent automatically analyzed performance and generated personalized learning path"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/student/{student_id}/progress", response_model=Dict[str, Any])
async def get_student_progress(
    student_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive progress summary for a student."""
    
    try:
        progress_summary = await assessment_analysis_service.get_student_progress_summary(student_id)
        
        logger.info(f"Retrieved progress summary for student {student_id}")
        return progress_summary
        
    except Exception as e:
        logger.error(f"Failed to get student progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get progress: {str(e)}"
        )

# ====================================================================
# LEARNING PATH ENDPOINTS  
# ====================================================================

@router.post("/generate-learning-path", response_model=Dict[str, Any])
async def generate_learning_path(
    path_request: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate a personalized learning path for a student.
    
    Expected format:
    {
        "student_id": "student_id",
        "target_subject": "Mathematics",
        "target_grade": 5,
        "learning_goals": ["Master addition", "Improve problem solving"],
        "include_recent_assessments": 3  // Number of recent assessments to consider
    }
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Extract request data
        student_id = path_request["student_id"]
        target_subject = path_request["target_subject"]
        target_grade = path_request["target_grade"]
        learning_goals = path_request.get("learning_goals", [])
        include_recent = path_request.get("include_recent_assessments", 3)
        
        # Get student's recent performance data
        progress_summary = await assessment_analysis_service.get_student_progress_summary(student_id)
        
        # Get recent performances (this would need to be implemented in the analysis service)
        recent_performances = []  # Placeholder - would get from progress_summary
        
        # Get current knowledge gaps
        knowledge_gaps = []  # Placeholder - would get from analysis service
        
        # Generate learning path
        learning_path = await learning_path_service.generate_personalized_learning_path(
            student_id=student_id,
            teacher_uid=teacher_uid,
            knowledge_gaps=knowledge_gaps,
            student_performances=recent_performances,
            target_subject=target_subject,
            target_grade=target_grade,
            learning_goals=learning_goals
        )
        
        logger.info(f"Generated learning path {learning_path.path_id} for student {student_id}")
        
        return {
            "path_id": learning_path.path_id,
            "title": learning_path.title,
            "description": learning_path.description,
            "total_steps": len(learning_path.steps),
            "estimated_duration_hours": learning_path.total_estimated_duration_minutes / 60,
            "learning_goals": learning_path.learning_goals,
            "addresses_gaps": len(learning_path.addresses_gaps),
            "steps_preview": [
                {
                    "step_number": step.step_number,
                    "title": step.title,
                    "topic": step.topic,
                    "difficulty": step.difficulty_level.value,
                    "estimated_minutes": step.estimated_duration_minutes
                }
                for step in learning_path.steps[:5]  # First 5 steps
            ],
            "path_created": True
        }
        
    except Exception as e:
        logger.error(f"Failed to generate learning path: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Path generation failed: {str(e)}"
        )

@router.get("/student/{student_id}/learning-paths", response_model=List[Dict[str, Any]])
async def get_student_learning_paths(
    student_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all learning paths for a student."""
    
    try:
        learning_paths = await learning_path_service.get_student_learning_paths(student_id)
        
        return [
            {
                "path_id": path.path_id,
                "title": path.title,
                "subject": path.subject,
                "completion_percentage": path.completion_percentage,
                "current_step": path.current_step,
                "total_steps": len(path.steps),
                "created_at": path.created_at.isoformat(),
                "estimated_duration_hours": path.total_estimated_duration_minutes / 60,
                "status": "completed" if path.completed_at else "in_progress" if path.started_at else "not_started"
            }
            for path in learning_paths
        ]
        
    except Exception as e:
        logger.error(f"Failed to get learning paths: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get learning paths: {str(e)}"
        )

@router.get("/learning-path/{path_id}", response_model=Dict[str, Any])
async def get_learning_path_details(
    path_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed information about a learning path."""
    
    try:
        learning_path = await learning_path_service.get_learning_path(path_id)
        
        if not learning_path:
            raise HTTPException(
                status_code=404,
                detail="Learning path not found"
            )
        
        return {
            "path_id": learning_path.path_id,
            "title": learning_path.title,
            "description": learning_path.description,
            "subject": learning_path.subject,
            "target_grade": learning_path.target_grade,
            "learning_goals": learning_path.learning_goals,
            "completion_percentage": learning_path.completion_percentage,
            "current_step": learning_path.current_step,
            "total_estimated_duration_minutes": learning_path.total_estimated_duration_minutes,
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_number": step.step_number,
                    "title": step.title,
                    "description": step.description,
                    "topic": step.topic,
                    "subtopic": step.subtopic,
                    "difficulty_level": step.difficulty_level.value,
                    "learning_objective": step.learning_objective.value,
                    "content_type": step.content_type,
                    "content_text": step.content_text,
                    "estimated_duration_minutes": step.estimated_duration_minutes,
                    "is_completed": step.is_completed,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "performance_score": step.performance_score
                }
                for step in learning_path.steps
            ],
            "created_at": learning_path.created_at.isoformat(),
            "last_updated": learning_path.last_updated.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get learning path details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get learning path: {str(e)}"
        )

@router.post("/learning-path/{path_id}/update-progress")
async def update_learning_path_progress(
    path_id: str,
    progress_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update progress on a learning path step.
    
    Expected format:
    {
        "step_id": "step_id",
        "completed": true,
        "performance_score": 85.5  // Optional
    }
    """
    
    try:
        step_id = progress_data["step_id"]
        completed = progress_data["completed"]
        performance_score = progress_data.get("performance_score")
        
        updated_path = await learning_path_service.update_learning_path_progress(
            path_id=path_id,
            step_id=step_id,
            completed=completed,
            performance_score=performance_score
        )
        
        logger.info(f"Updated progress for path {path_id}, step {step_id}")
        
        return {
            "path_id": path_id,
            "step_id": step_id,
            "completed": completed,
            "new_completion_percentage": updated_path.completion_percentage,
            "current_step": updated_path.current_step,
            "is_path_completed": updated_path.completed_at is not None,
            "update_successful": True
        }
        
    except Exception as e:
        logger.error(f"Failed to update learning path progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Progress update failed: {str(e)}"
        )

# ====================================================================
# ADAPTIVE LEARNING ENDPOINTS
# ====================================================================

@router.post("/adapt-learning-path/{path_id}")
async def adapt_learning_path(
    path_id: str,
    adaptation_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Adapt a learning path based on new assessment results.
    
    Expected format:
    {
        "new_assessment_id": "assessment_id",
        "student_answers": [0, 1, 2],
        "time_taken_minutes": 20
    }
    """
    
    try:
        # Get new assessment performance
        assessment_id = adaptation_data["new_assessment_id"]
        student_answers = adaptation_data["student_answers"]
        time_taken = adaptation_data["time_taken_minutes"]
        
        # Get assessment and analyze performance
        assessment = await enhanced_assessment_service.get_assessment_by_id(assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get current learning path
        current_path = await learning_path_service.get_learning_path(path_id)
        if not current_path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        # Analyze new performance
        new_performance = await assessment_analysis_service.analyze_assessment_performance(
            student_id=current_path.student_id,
            assessment=assessment,
            student_answers=student_answers,
            time_taken_minutes=time_taken
        )
        
        # Get new knowledge gaps (placeholder - would be implemented in analysis service)
        new_gaps = []  # This would come from the analysis service
        
        # Adapt the learning path
        adapted_path = await learning_path_service.adapt_learning_path(
            path_id=path_id,
            new_performance_data=new_performance,
            new_gaps=new_gaps
        )
        
        logger.info(f"Adapted learning path {path_id} based on assessment {assessment_id}")
        
        return {
            "path_id": path_id,
            "assessment_analyzed": assessment_id,
            "new_performance_score": new_performance.score_percentage,
            "adaptation_applied": True,
            "new_total_steps": len(adapted_path.steps),
            "adaptation_summary": adapted_path.adaptation_history[-1] if adapted_path.adaptation_history else None
        }
        
    except Exception as e:
        logger.error(f"Failed to adapt learning path: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Adaptation failed: {str(e)}"
        )

# ====================================================================
# ANALYTICS AND INSIGHTS ENDPOINTS
# ====================================================================

@router.get("/teacher/learning-analytics", response_model=Dict[str, Any])
async def get_teacher_learning_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get learning analytics overview for a teacher."""
    teacher_uid = current_user["uid"]
    
    try:
        # This would aggregate data across all students
        # For now, return placeholder analytics
        
        analytics = {
            "teacher_uid": teacher_uid,
            "total_students_with_paths": 0,  # Would be calculated
            "total_active_paths": 0,
            "average_completion_rate": 0.0,
            "most_common_knowledge_gaps": [],
            "subject_performance_trends": {},
            "learning_path_effectiveness": {
                "paths_completed": 0,
                "average_improvement": 0.0,
                "student_satisfaction": 0.0
            },
            "recommendations_for_teacher": [
                "Create more assessments to gather learning data",
                "Upload subject-specific content for better RAG generation",
                "Review student progress regularly"
            ]
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get learning analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analytics retrieval failed: {str(e)}"
        )

@router.get("/student/{student_id}/learning-insights", response_model=Dict[str, Any])
async def get_student_learning_insights(
    student_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed learning insights for a specific student."""
    
    try:
        # Get comprehensive student data
        progress_summary = await assessment_analysis_service.get_student_progress_summary(student_id)
        learning_paths = await learning_path_service.get_student_learning_paths(student_id)
        
        # Calculate insights
        insights = {
            "student_id": student_id,
            "learning_velocity": "steady",  # Would be calculated from progress data
            "strength_areas": progress_summary.get("subject_performance", {}),
            "improvement_areas": [],  # Would come from gap analysis
            "learning_style_indicators": {
                "prefers_visual": False,
                "needs_more_time": False,
                "learns_better_with_examples": True
            },
            "engagement_metrics": {
                "path_completion_rate": 0.0,
                "average_step_time": 0,
                "consistency_score": 0.0
            },
            "next_recommended_actions": [
                "Continue with current learning path",
                "Take assessment to validate progress",
                "Review challenging topics"
            ],
            "achievement_milestones": [],
            "learning_path_summary": {
                "total_paths": len(learning_paths),
                "active_paths": len([p for p in learning_paths if not p.completed_at]),
                "completed_paths": len([p for p in learning_paths if p.completed_at])
            }
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get student insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Insights retrieval failed: {str(e)}"
        )
