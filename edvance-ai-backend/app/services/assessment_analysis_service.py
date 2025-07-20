# FILE: app/services/assessment_analysis_service.py

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from app.models.learning_models import (
    StudentPerformance, KnowledgeGap, LearningObjectiveType, 
    DifficultyLevel, LearningRecommendation
)
from app.models.student import Assessment, AssessmentQuestion
from app.core.firebase import db
from app.core.vertex import get_vertex_model

logger = logging.getLogger(__name__)

class AssessmentAnalysisService:
    """Service for analyzing student assessment performance and identifying learning needs."""
    
    def __init__(self):
        self.model = get_vertex_model("gemini-2.5-pro")
        self.performances_collection = "student_performances"
        self.knowledge_gaps_collection = "knowledge_gaps"
        self.recommendations_collection = "learning_recommendations"
    
    async def analyze_assessment_performance(
        self, 
        student_id: str,
        assessment: Assessment,
        student_answers: List[int],
        time_taken_minutes: int
    ) -> StudentPerformance:
        """Analyze a student's performance on an assessment."""
        
        try:
            logger.info(f"Analyzing assessment performance for student {student_id}")
            
            # Calculate basic metrics
            total_questions = len(assessment.questions)
            correct_answers = sum(1 for i, answer in enumerate(student_answers) 
                                if i < len(assessment.questions) and answer == assessment.questions[i].correct_answer)
            score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            # Analyze performance by question
            question_performances = []
            topic_scores = defaultdict(list)
            difficulty_scores = defaultdict(list)
            
            for i, (question, student_answer) in enumerate(zip(assessment.questions, student_answers)):
                is_correct = student_answer == question.correct_answer
                
                question_performance = {
                    "question_id": question.question_id,
                    "question_text": question.question_text,
                    "student_answer": student_answer,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "topic": question.topic,
                    "difficulty": question.difficulty,
                    "time_spent_seconds": (time_taken_minutes * 60) // total_questions  # Rough estimate
                }
                question_performances.append(question_performance)
                
                # Group by topic and difficulty
                topic_scores[question.topic].append(1 if is_correct else 0)
                difficulty_scores[question.difficulty].append(1 if is_correct else 0)
            
            # Calculate topic and difficulty scores
            topic_score_averages = {
                topic: sum(scores) / len(scores) * 100 
                for topic, scores in topic_scores.items()
            }
            difficulty_score_averages = {
                difficulty: sum(scores) / len(scores) * 100 
                for difficulty, scores in difficulty_scores.items()
            }
            
            # Identify strengths and weaknesses
            strengths = [topic for topic, score in topic_score_averages.items() if score >= 80]
            weaknesses = [topic for topic, score in topic_score_averages.items() if score < 60]
            
            # Create performance record
            performance = StudentPerformance(
                performance_id=str(uuid.uuid4()),
                student_id=student_id,
                assessment_id=assessment.assessment_id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                score_percentage=score_percentage,
                time_taken_minutes=time_taken_minutes,
                question_performances=question_performances,
                topic_scores=topic_score_averages,
                difficulty_scores=difficulty_score_averages,
                learning_objective_scores={},  # Will be enhanced with AI analysis
                strengths=strengths,
                weaknesses=weaknesses,
                recommended_focus_areas=weaknesses  # Initial recommendation
            )
            
            # Save performance to Firestore
            await self._save_performance(performance)
            
            # Generate detailed analysis using AI
            enhanced_performance = await self._enhance_performance_with_ai(performance, assessment)
            
            # Identify knowledge gaps
            knowledge_gaps = await self.identify_knowledge_gaps(enhanced_performance, assessment)
            
            # Generate learning recommendations
            recommendations = await self.generate_learning_recommendations(
                student_id, enhanced_performance, knowledge_gaps
            )
            
            logger.info(f"Completed analysis for student {student_id}: {score_percentage:.1f}% score, {len(knowledge_gaps)} gaps identified")
            
            return enhanced_performance
            
        except Exception as e:
            logger.error(f"Failed to analyze assessment performance: {str(e)}")
            raise e
    
    async def _enhance_performance_with_ai(
        self, 
        performance: StudentPerformance,
        assessment: Assessment
    ) -> StudentPerformance:
        """Use AI to enhance performance analysis with deeper insights."""
        
        try:
            # Prepare analysis prompt
            prompt = f"""You are an expert educational analyst. Analyze this student's assessment performance and provide detailed insights.

ASSESSMENT INFORMATION:
- Subject: {assessment.subject}
- Topic: {assessment.topic}
- Grade Level: {assessment.grade}
- Difficulty: {assessment.difficulty}
- Total Questions: {performance.total_questions}

STUDENT PERFORMANCE:
- Overall Score: {performance.score_percentage:.1f}%
- Correct Answers: {performance.correct_answers}/{performance.total_questions}
- Time Taken: {performance.time_taken_minutes} minutes

QUESTION-BY-QUESTION ANALYSIS:
{self._format_question_analysis(performance.question_performances)}

TOPIC PERFORMANCE:
{self._format_topic_scores(performance.topic_scores)}

DIFFICULTY PERFORMANCE:
{self._format_difficulty_scores(performance.difficulty_scores)}

Please provide a detailed analysis in JSON format:

{{
  "learning_objective_scores": {{
    "remember": score_0_to_100,
    "understand": score_0_to_100,
    "apply": score_0_to_100,
    "analyze": score_0_to_100,
    "evaluate": score_0_to_100,
    "create": score_0_to_100
  }},
  "detailed_strengths": ["specific strength 1", "specific strength 2"],
  "detailed_weaknesses": ["specific weakness 1", "specific weakness 2"],
  "learning_patterns": ["pattern 1", "pattern 2"],
  "recommended_focus_areas": ["focus area 1", "focus area 2"],
  "next_steps": ["specific action 1", "specific action 2"],
  "confidence_indicators": ["indicator 1", "indicator 2"],
  "improvement_suggestions": ["suggestion 1", "suggestion 2"]
}}"""

            # Get AI analysis
            response = self.model.generate_content(prompt)
            ai_analysis = self._parse_ai_analysis(response.text)
            
            # Update performance with AI insights
            performance.learning_objective_scores = ai_analysis.get("learning_objective_scores", {})
            performance.strengths = ai_analysis.get("detailed_strengths", performance.strengths)
            performance.weaknesses = ai_analysis.get("detailed_weaknesses", performance.weaknesses)
            performance.recommended_focus_areas = ai_analysis.get("recommended_focus_areas", performance.recommended_focus_areas)
            
            # Add AI analysis metadata
            performance.question_performances.append({
                "ai_analysis": {
                    "learning_patterns": ai_analysis.get("learning_patterns", []),
                    "next_steps": ai_analysis.get("next_steps", []),
                    "confidence_indicators": ai_analysis.get("confidence_indicators", []),
                    "improvement_suggestions": ai_analysis.get("improvement_suggestions", [])
                }
            })
            
            # Update in Firestore
            await self._save_performance(performance)
            
            return performance
            
        except Exception as e:
            logger.warning(f"AI enhancement failed, using basic analysis: {str(e)}")
            return performance
    
    async def identify_knowledge_gaps(
        self, 
        performance: StudentPerformance,
        assessment: Assessment
    ) -> List[KnowledgeGap]:
        """Identify specific knowledge gaps from performance analysis."""
        
        try:
            gaps = []
            
            # Analyze incorrect answers for patterns
            incorrect_questions = [
                (q_perf, next((q for q in assessment.questions if q.question_id == q_perf["question_id"]), None))
                for q_perf in performance.question_performances
                if isinstance(q_perf, dict) and not q_perf.get("is_correct", True)
            ]
            
            # Group by topic and difficulty
            topic_gaps = defaultdict(list)
            for q_perf, question in incorrect_questions:
                if question:
                    topic_gaps[question.topic].append((q_perf, question))
            
            # Create gap records for topics with multiple incorrect answers
            for topic, topic_questions in topic_gaps.items():
                if len(topic_questions) >= 2:  # Multiple mistakes in same topic
                    gap = KnowledgeGap(
                        gap_id=str(uuid.uuid4()),
                        student_id=performance.student_id,
                        subject=assessment.subject,
                        topic=topic,
                        difficulty_level=DifficultyLevel(assessment.difficulty),
                        learning_objective=LearningObjectiveType.UNDERSTAND,  # Default, will be refined
                        confidence_score=min(0.9, len(topic_questions) / len(assessment.questions)),
                        severity_score=1.0 - (performance.topic_scores.get(topic, 0) / 100),
                        frequency=len(topic_questions),
                        source_assessments=[assessment.assessment_id],
                        related_questions=[q_perf["question_id"] for q_perf, _ in topic_questions]
                    )
                    gaps.append(gap)
            
            # Save gaps to Firestore
            for gap in gaps:
                await self._save_knowledge_gap(gap)
            
            logger.info(f"Identified {len(gaps)} knowledge gaps for student {performance.student_id}")
            return gaps
            
        except Exception as e:
            logger.error(f"Failed to identify knowledge gaps: {str(e)}")
            return []
    
    async def generate_learning_recommendations(
        self,
        student_id: str,
        performance: StudentPerformance,
        knowledge_gaps: List[KnowledgeGap]
    ) -> List[LearningRecommendation]:
        """Generate personalized learning recommendations."""
        
        try:
            recommendations = []
            
            # Create recommendations for each knowledge gap
            for gap in knowledge_gaps:
                if gap.severity_score > 0.3:  # Only for significant gaps
                    recommendation = LearningRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        student_id=student_id,
                        title=f"Improve {gap.topic} Understanding",
                        description=f"Focus on strengthening your understanding of {gap.topic} concepts",
                        rationale=f"You had difficulty with {gap.frequency} questions on {gap.topic}",
                        recommended_action=f"Practice {gap.topic} problems at {gap.difficulty_level.value} level",
                        content_type="practice_problems",
                        difficulty_level=gap.difficulty_level,
                        estimated_duration_minutes=30,
                        priority_score=gap.severity_score,
                        urgency_level="medium" if gap.severity_score > 0.7 else "low",
                        based_on_assessments=[performance.assessment_id],
                        addresses_gaps=[gap.gap_id]
                    )
                    recommendations.append(recommendation)
            
            # Generate general recommendations based on performance
            if performance.score_percentage < 70:
                general_rec = LearningRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    student_id=student_id,
                    title="Review Fundamental Concepts",
                    description="Strengthen your foundation in this subject area",
                    rationale=f"Overall score of {performance.score_percentage:.1f}% suggests need for review",
                    recommended_action="Review basic concepts and practice easier problems first",
                    content_type="review_materials",
                    difficulty_level=DifficultyLevel.EASY,
                    estimated_duration_minutes=45,
                    priority_score=0.8,
                    urgency_level="high",
                    based_on_assessments=[performance.assessment_id],
                    addresses_gaps=[gap.gap_id for gap in knowledge_gaps]
                )
                recommendations.append(general_rec)
            
            # Save recommendations
            for rec in recommendations:
                await self._save_recommendation(rec)
            
            logger.info(f"Generated {len(recommendations)} learning recommendations for student {student_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return []
    
    async def get_student_progress_summary(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive progress summary for a student."""
        
        try:
            # Get recent performances - handling Firestore index requirement
            try:
                # Try with ordering (requires composite index)
                performances_query = (db.collection(self.performances_collection)
                                    .where("student_id", "==", student_id)
                                    .order_by("completed_at", direction="DESCENDING")
                                    .limit(10))
                
                performance_docs = performances_query.get()
                performances = [StudentPerformance(**doc.to_dict()) for doc in performance_docs]
                
            except Exception as index_error:
                logger.warning(f"Composite index not available, falling back to simple query: {index_error}")
                # Fallback: Get all performances for student and sort in Python
                performances_query = (db.collection(self.performances_collection)
                                    .where("student_id", "==", student_id))
                
                performance_docs = performances_query.get()
                all_performances = [StudentPerformance(**doc.to_dict()) for doc in performance_docs]
                
                # Sort by completed_at in Python and limit to 10
                performances = sorted(
                    all_performances, 
                    key=lambda p: p.completed_at if p.completed_at else datetime.min, 
                    reverse=True
                )[:10]
            
            # Get active knowledge gaps
            try:
                gaps_query = (db.collection(self.knowledge_gaps_collection)
                             .where("student_id", "==", student_id))
                
                gap_docs = gaps_query.get()
                gaps = [KnowledgeGap(**doc.to_dict()) for doc in gap_docs]
            except Exception as e:
                logger.warning(f"Failed to get knowledge gaps for {student_id}: {e}")
                gaps = []
            
            # Get active recommendations
            try:
                recs_query = (db.collection(self.recommendations_collection)
                             .where("student_id", "==", student_id)
                             .where("is_active", "==", True))
                
                rec_docs = recs_query.get()
                recommendations = [LearningRecommendation(**doc.to_dict()) for doc in rec_docs]
            except Exception as e:
                logger.warning(f"Failed to get recommendations for {student_id}: {e}")
                recommendations = []
            
            # Calculate progress metrics
            if performances:
                avg_score = sum(p.score_percentage for p in performances) / len(performances)
                score_trend = self._calculate_score_trend(performances)
                subject_performance = self._aggregate_subject_performance(performances)
            else:
                avg_score = 0
                score_trend = "no_data"
                subject_performance = {}
            
            return {
                "student_id": student_id,
                "average_score": round(avg_score, 1),
                "score_trend": score_trend,
                "total_assessments": len(performances),
                "active_knowledge_gaps": len(gaps),
                "active_recommendations": len(recommendations),
                "subject_performance": subject_performance,
                "recent_performances": [p.dict() for p in performances[:5]],
                "priority_gaps": [g.dict() for g in gaps if g.severity_score > 0.7],
                "top_recommendations": [r.dict() for r in recommendations[:3]],
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get progress summary for {student_id}: {str(e)}")
            return {"error": str(e)}
    
    # Helper methods
    def _format_question_analysis(self, performances: List[Dict[str, Any]]) -> str:
        """Format question performance for AI analysis."""
        formatted = []
        for i, perf in enumerate(performances):
            if isinstance(perf, dict) and "question_id" in perf:
                status = "✓ Correct" if perf.get("is_correct") else "✗ Incorrect"
                formatted.append(f"Q{i+1}: {status} - Topic: {perf.get('topic', 'Unknown')} - Difficulty: {perf.get('difficulty', 'Unknown')}")
        return "\\n".join(formatted)
    
    def _format_topic_scores(self, topic_scores: Dict[str, float]) -> str:
        """Format topic scores for display."""
        return "\\n".join([f"{topic}: {score:.1f}%" for topic, score in topic_scores.items()])
    
    def _format_difficulty_scores(self, difficulty_scores: Dict[str, float]) -> str:
        """Format difficulty scores for display."""
        return "\\n".join([f"{difficulty}: {score:.1f}%" for difficulty, score in difficulty_scores.items()])
    
    def _parse_ai_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse AI analysis response."""
        try:
            import json
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                return json.loads(json_text)
            
            return {}
        except Exception as e:
            logger.warning(f"Failed to parse AI analysis: {str(e)}")
            return {}
    
    def _calculate_score_trend(self, performances: List[StudentPerformance]) -> str:
        """Calculate if scores are improving, declining, or stable."""
        if len(performances) < 2:
            return "insufficient_data"
        
        recent_scores = [p.score_percentage for p in performances[:3]]
        older_scores = [p.score_percentage for p in performances[3:6]]
        
        if not older_scores:
            return "insufficient_data"
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 5:
            return "improving"
        elif recent_avg < older_avg - 5:
            return "declining"
        else:
            return "stable"
    
    def _aggregate_subject_performance(self, performances: List[StudentPerformance]) -> Dict[str, float]:
        """Aggregate performance by subject."""
        subject_scores = defaultdict(list)
        
        for perf in performances:
            # We'd need to get the assessment to know the subject
            # For now, use a placeholder
            subject_scores["general"].append(perf.score_percentage)
        
        return {
            subject: sum(scores) / len(scores)
            for subject, scores in subject_scores.items()
        }
    
    async def _save_performance(self, performance: StudentPerformance) -> None:
        """Save performance to Firestore."""
        doc_ref = db.collection(self.performances_collection).document(performance.performance_id)
        doc_ref.set(performance.dict())
    
    async def _save_knowledge_gap(self, gap: KnowledgeGap) -> None:
        """Save knowledge gap to Firestore."""
        doc_ref = db.collection(self.knowledge_gaps_collection).document(gap.gap_id)
        doc_ref.set(gap.dict())
    
    async def _save_recommendation(self, recommendation: LearningRecommendation) -> None:
        """Save recommendation to Firestore."""
        doc_ref = db.collection(self.recommendations_collection).document(recommendation.recommendation_id)
        doc_ref.set(recommendation.dict())

# Global instance
assessment_analysis_service = AssessmentAnalysisService()
