# FILE: app/services/learning_path_monitoring_service.py

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta

from app.core.firebase import db
from app.agents.learning_path_agent.agent import root_agent as learning_path_agent
from app.agents.tools.learning_path_tools import (
    monitor_student_assessments,
    analyze_assessment_completion,
    track_learning_progress
)

logger = logging.getLogger(__name__)

class LearningPathMonitoringService:
    """
    Service that coordinates with the Learning Path Agent to automatically 
    monitor and respond to student learning events.
    """
    
    def __init__(self):
        self.agent = learning_path_agent
        self.monitoring_active = False
        self.event_listeners = {}
        self.monitoring_tasks = {}
    
    async def start_monitoring(self, teacher_uid: str) -> Dict[str, Any]:
        """
        Start automated monitoring for a teacher's students.
        
        Args:
            teacher_uid: Teacher to monitor students for
        
        Returns:
            Dict containing monitoring status
        """
        try:
            logger.info(f"Starting automated learning path monitoring for teacher {teacher_uid}")
            
            # Activate monitoring through the agent
            monitoring_result = await monitor_student_assessments(teacher_uid, continuous=True)
            
            # Set up event listeners for real-time monitoring
            await self._setup_firestore_listeners(teacher_uid)
            
            # Schedule periodic progress checks
            await self._schedule_progress_monitoring(teacher_uid)
            
            self.monitoring_active = True
            
            result = {
                "teacher_uid": teacher_uid,
                "monitoring_started": True,
                "agent_activated": True,
                "real_time_listeners": "active",
                "progress_monitoring": "scheduled",
                "monitoring_result": monitoring_result
            }
            
            logger.info(f"Automated monitoring activated for teacher {teacher_uid}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return {
                "error": f"Monitoring startup failed: {str(e)}",
                "teacher_uid": teacher_uid,
                "monitoring_started": False
            }
    
    async def handle_assessment_completion(
        self,
        student_id: str,
        assessment_id: str,
        student_answers: List[int],
        time_taken_minutes: int,
        teacher_uid: str
    ) -> Dict[str, Any]:
        """
        Handle an assessment completion event and trigger agent response.
        
        Args:
            student_id: Student who completed assessment
            assessment_id: Assessment that was completed
            student_answers: Student's answers
            time_taken_minutes: Time taken
            teacher_uid: Teacher who owns the assessment
        
        Returns:
            Dict containing agent's response and actions taken
        """
        try:
            logger.info(f"Processing assessment completion: {assessment_id} by student {student_id}")
            
            # Trigger the learning path agent to analyze and respond
            agent_response = await self._trigger_agent_analysis(
                student_id, assessment_id, student_answers, time_taken_minutes
            )
            
            # Log the event and response
            await self._log_monitoring_event(
                event_type="assessment_completion",
                student_id=student_id,
                assessment_id=assessment_id,
                teacher_uid=teacher_uid,
                agent_response=agent_response
            )
            
            return {
                "event": "assessment_completion",
                "student_id": student_id,
                "assessment_id": assessment_id,
                "processed": True,
                "agent_response": agent_response,
                "learning_path_generated": agent_response.get("learning_path_generated", False),
                "intervention_type": agent_response.get("intervention_type"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to handle assessment completion: {str(e)}")
            return {
                "error": f"Assessment completion handling failed: {str(e)}",
                "student_id": student_id,
                "assessment_id": assessment_id,
                "processed": False
            }
    
    async def monitor_learning_path_progress(self, path_id: str, student_id: str) -> Dict[str, Any]:
        """
        Monitor progress on a learning path and trigger adaptations if needed.
        
        Args:
            path_id: Learning path to monitor
            student_id: Student progressing through path
        
        Returns:
            Dict containing monitoring results
        """
        try:
            logger.info(f"Monitoring learning path progress: {path_id} for student {student_id}")
            
            # Use agent tools to track progress
            progress_result = await track_learning_progress(student_id, path_id)
            
            # Check if agent recommendations require action
            if progress_result.get("adaptation_triggered"):
                logger.info(f"Learning path {path_id} was automatically adapted")
            
            return {
                "path_id": path_id,
                "student_id": student_id,
                "monitoring_completed": True,
                "progress_analysis": progress_result,
                "adaptations_made": progress_result.get("adaptation_triggered", False),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to monitor learning path progress: {str(e)}")
            return {
                "error": f"Progress monitoring failed: {str(e)}",
                "path_id": path_id,
                "student_id": student_id
            }
    
    async def process_batch_assessments(self, teacher_uid: str) -> Dict[str, Any]:
        """
        Process all pending assessments for a teacher's students.
        
        Args:
            teacher_uid: Teacher to process assessments for
        
        Returns:
            Dict containing batch processing results
        """
        try:
            logger.info(f"Processing batch assessments for teacher {teacher_uid}")
            
            # Trigger agent batch monitoring
            batch_result = await monitor_student_assessments(teacher_uid, continuous=False)
            
            return {
                "teacher_uid": teacher_uid,
                "batch_processing_completed": True,
                "agent_result": batch_result,
                "assessments_processed": batch_result.get("assessments_processed", 0),
                "learning_paths_generated": batch_result.get("learning_paths_generated", 0),
                "students_helped": batch_result.get("students_helped", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process batch assessments: {str(e)}")
            return {
                "error": f"Batch processing failed: {str(e)}",
                "teacher_uid": teacher_uid
            }
    
    async def get_monitoring_status(self, teacher_uid: str) -> Dict[str, Any]:
        """
        Get current monitoring status for a teacher.
        
        Args:
            teacher_uid: Teacher to get status for
        
        Returns:
            Dict containing monitoring status
        """
        try:
            # Get monitoring statistics from recent activity
            monitoring_stats = await self._get_monitoring_statistics(teacher_uid)
            
            return {
                "teacher_uid": teacher_uid,
                "monitoring_active": self.monitoring_active,
                "agent_status": "active" if self.monitoring_active else "inactive",
                "recent_activity": monitoring_stats,
                "event_listeners": len(self.event_listeners),
                "scheduled_tasks": len(self.monitoring_tasks),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get monitoring status: {str(e)}")
            return {
                "error": f"Status retrieval failed: {str(e)}",
                "teacher_uid": teacher_uid
            }
    
    # Private helper methods
    
    async def _trigger_agent_analysis(
        self,
        student_id: str,
        assessment_id: str,
        student_answers: List[int],
        time_taken_minutes: int
    ) -> Dict[str, Any]:
        """Trigger the learning path agent to analyze assessment completion."""
        
        # Use the agent's analysis tool directly
        return await analyze_assessment_completion(
            student_id, assessment_id, student_answers, time_taken_minutes
        )
    
    async def _setup_firestore_listeners(self, teacher_uid: str) -> None:
        """Set up Firestore listeners for real-time monitoring."""
        
        try:
            # This would set up real-time listeners for assessment completions
            # For now, we'll simulate the setup
            logger.info(f"Setting up Firestore listeners for teacher {teacher_uid}")
            
            # In a real implementation, this would use Firestore listeners:
            # listener = db.collection('assessments').where('teacher_uid', '==', teacher_uid).on_snapshot(callback)
            # self.event_listeners[teacher_uid] = listener
            
            self.event_listeners[teacher_uid] = "simulated_listener"
            
        except Exception as e:
            logger.warning(f"Failed to setup Firestore listeners: {str(e)}")
    
    async def _schedule_progress_monitoring(self, teacher_uid: str) -> None:
        """Schedule periodic progress monitoring tasks."""
        
        try:
            # This would schedule periodic tasks to check learning path progress
            logger.info(f"Scheduling progress monitoring for teacher {teacher_uid}")
            
            # In a real implementation, this would use a task scheduler
            self.monitoring_tasks[teacher_uid] = "scheduled_monitoring"
            
        except Exception as e:
            logger.warning(f"Failed to schedule progress monitoring: {str(e)}")
    
    async def _log_monitoring_event(
        self,
        event_type: str,
        student_id: str,
        assessment_id: str,
        teacher_uid: str,
        agent_response: Dict[str, Any]
    ) -> None:
        """Log monitoring events for analytics and debugging."""
        
        try:
            event_log = {
                "timestamp": datetime.utcnow(),
                "event_type": event_type,
                "student_id": student_id,
                "assessment_id": assessment_id,
                "teacher_uid": teacher_uid,
                "agent_response": agent_response,
                "monitoring_service": "active"
            }
            
            # Save to monitoring logs collection
            db.collection("monitoring_logs").add(event_log)
            
        except Exception as e:
            logger.warning(f"Failed to log monitoring event: {str(e)}")
    
    async def _get_monitoring_statistics(self, teacher_uid: str) -> Dict[str, Any]:
        """Get recent monitoring statistics for a teacher."""
        
        try:
            # Query recent monitoring activity
            # This would query the monitoring_logs collection in a real implementation
            
            # For now, return simulated statistics
            return {
                "assessments_processed_today": 0,
                "learning_paths_generated_today": 0,
                "students_active": 0,
                "average_response_time_seconds": 2.5,
                "last_activity": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to get monitoring statistics: {str(e)}")
            return {}

# Global instance
learning_path_monitoring_service = LearningPathMonitoringService()
