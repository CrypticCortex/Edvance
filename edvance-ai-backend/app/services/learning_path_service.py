# FILE: app/services/learning_path_service.py

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.models.learning_models import (
    LearningPath, LearningStep, KnowledgeGap, StudentPerformance,
    DifficultyLevel, LearningObjectiveType, LearningRecommendation
)
from app.core.firebase import db
from app.core.vertex import get_vertex_model
from app.core.language import SupportedLanguage, validate_language, create_language_prompt_prefix, get_language_name

logger = logging.getLogger(__name__)

class LearningPathService:
    """Service for generating and managing personalized learning paths."""
    
    def __init__(self):
        self.model = get_vertex_model("gemini-2.5-pro")
        self.learning_paths_collection = "learning_paths"
        self.content_library_collection = "learning_content"
    
    async def generate_personalized_learning_path(
        self,
        student_id: str,
        teacher_uid: str,
        knowledge_gaps: List[KnowledgeGap],
        student_performances: List[StudentPerformance],
        target_subject: str,
        target_grade: int,
        learning_goals: Optional[List[str]] = None,
        language: str = "english"
    ) -> LearningPath:
        """Generate a personalized learning path based on assessment analysis."""
        
        try:
            logger.info(f"Generating learning path for student {student_id} in {target_subject}")
            
            # Analyze student's current state
            current_state = await self._analyze_student_current_state(
                student_id, knowledge_gaps, student_performances
            )
            
            # Validate and normalize language
            validated_language = validate_language(language)
            logger.info(f"Generating learning path for student {student_id} in {target_subject} using {validated_language}")
            
            # Generate learning steps using AI
            learning_steps = await self._generate_learning_steps_with_ai(
                current_state, knowledge_gaps, target_subject, target_grade, learning_goals, validated_language
            )
            
            # Create learning path
            path_id = str(uuid.uuid4())
            learning_path = LearningPath(
                path_id=path_id,
                student_id=student_id,
                teacher_uid=teacher_uid,
                title=f"Personalized {target_subject} Learning Path",
                description=f"Customized learning journey to address knowledge gaps and achieve learning goals",
                subject=target_subject,
                target_grade=target_grade,
                learning_goals=learning_goals or self._generate_default_learning_goals(knowledge_gaps),
                addresses_gaps=[gap.gap_id for gap in knowledge_gaps],
                steps=learning_steps,
                total_estimated_duration_minutes=sum(step.estimated_duration_minutes for step in learning_steps),
                source_assessments=[gap.source_assessments[0] for gap in knowledge_gaps if gap.source_assessments]
            )
            
            # Save to Firestore
            await self._save_learning_path(learning_path)
            
            # Generate lessons for each learning step
            await self._generate_lessons_for_steps(learning_path)
            
            logger.info(f"Generated learning path {path_id} with {len(learning_steps)} steps and lessons")
            return learning_path
            
        except Exception as e:
            logger.error(f"Failed to generate learning path: {str(e)}")
            raise e
    
    async def _analyze_student_current_state(
        self,
        student_id: str,
        knowledge_gaps: List[KnowledgeGap],
        performances: List[StudentPerformance]
    ) -> Dict[str, Any]:
        """Analyze student's current learning state."""
        
        try:
            # Calculate current proficiency levels
            topic_proficiencies = {}
            difficulty_comfort = {}
            learning_style_indicators = {}
            
            if performances:
                # Aggregate topic performance
                for perf in performances:
                    for topic, score in perf.topic_scores.items():
                        if topic not in topic_proficiencies:
                            topic_proficiencies[topic] = []
                        topic_proficiencies[topic].append(score)
                
                # Average scores by topic
                topic_proficiencies = {
                    topic: sum(scores) / len(scores)
                    for topic, scores in topic_proficiencies.items()
                }
                
                # Aggregate difficulty comfort
                for perf in performances:
                    for difficulty, score in perf.difficulty_scores.items():
                        if difficulty not in difficulty_comfort:
                            difficulty_comfort[difficulty] = []
                        difficulty_comfort[difficulty].append(score)
                
                difficulty_comfort = {
                    difficulty: sum(scores) / len(scores)
                    for difficulty, scores in difficulty_comfort.items()
                }
                
                # Analyze learning patterns
                avg_time = sum(p.time_taken_minutes for p in performances) / len(performances)
                avg_score = sum(p.score_percentage for p in performances) / len(performances)
                
                learning_style_indicators = {
                    "prefers_time": "extended" if avg_time > 45 else "standard",
                    "current_level": "advanced" if avg_score > 85 else "intermediate" if avg_score > 65 else "beginner",
                    "consistency": "high" if max(p.score_percentage for p in performances) - min(p.score_percentage for p in performances) < 20 else "variable"
                }
            
            # Analyze knowledge gaps
            gap_analysis = {
                "critical_gaps": [gap for gap in knowledge_gaps if gap.severity_score > 0.8],
                "moderate_gaps": [gap for gap in knowledge_gaps if 0.5 < gap.severity_score <= 0.8],
                "minor_gaps": [gap for gap in knowledge_gaps if gap.severity_score <= 0.5],
                "primary_subjects": list(set(gap.subject for gap in knowledge_gaps)),
                "difficulty_gaps": list(set(gap.difficulty_level for gap in knowledge_gaps))
            }
            
            return {
                "student_id": student_id,
                "topic_proficiencies": topic_proficiencies,
                "difficulty_comfort": difficulty_comfort,
                "learning_style_indicators": learning_style_indicators,
                "gap_analysis": gap_analysis,
                "total_assessments": len(performances),
                "overall_performance": sum(p.score_percentage for p in performances) / len(performances) if performances else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze student state: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_learning_steps_with_ai(
        self,
        current_state: Dict[str, Any],
        knowledge_gaps: List[KnowledgeGap],
        subject: str,
        grade: int,
        learning_goals: Optional[List[str]],
        language: SupportedLanguage
    ) -> List[LearningStep]:
        """Use AI to generate personalized learning steps."""
        
        try:
            # Create language-aware prompt
            language_prefix = create_language_prompt_prefix(language, "Personalized learning path generation")
            
            # Prepare prompt for AI
            prompt = f"""{language_prefix}

You are an expert educational path designer. Create a personalized learning sequence for a student based on their current state and knowledge gaps.

STUDENT CURRENT STATE:
- Grade Level: {grade}
- Subject: {subject}
- Overall Performance: {current_state.get('overall_performance', 0):.1f}%
- Learning Style: {current_state.get('learning_style_indicators', {})}
- Topic Proficiencies: {current_state.get('topic_proficiencies', {})}
- Difficulty Comfort: {current_state.get('difficulty_comfort', {})}

KNOWLEDGE GAPS TO ADDRESS:
{self._format_knowledge_gaps_for_ai(knowledge_gaps)}

LEARNING GOALS:
{learning_goals or ['Improve understanding in identified weak areas', 'Build confidence in the subject']}

Create a sequence of 8-12 learning steps that will systematically address the knowledge gaps and help the student achieve their learning goals. Each step should build on the previous ones.

🚨 CRITICAL TECHNICAL FIELD REQUIREMENTS 🚨
YOU MUST USE THESE EXACT ENGLISH VALUES - DO NOT TRANSLATE THESE FIELDS:

difficulty_level: MUST be exactly one of these English words:
- "beginner" (for basic/introductory content)
- "easy" (for simple concepts)  
- "medium" (for moderate difficulty)
- "hard" (for challenging content)
- "advanced" (for expert level)

learning_objective: MUST be exactly one of these English words:
- "remember" (for memorization/recall)
- "understand" (for comprehension)
- "apply" (for using knowledge)
- "analyze" (for breaking down concepts)
- "evaluate" (for making judgments)
- "create" (for producing new content)

content_type: MUST be exactly one of these English words:
- "explanation" (for teaching concepts)
- "practice" (for exercises)
- "video" (for video content)
- "reading" (for text materials)
- "interactive" (for hands-on activities)

⚠️ LANGUAGE REQUIREMENTS:
- Generate ALL content (titles, descriptions, content_text) in {get_language_name(language)}
- But keep the three technical fields above in English exactly as specified
- Do NOT translate "beginner", "easy", "medium", "hard", "advanced"
- Do NOT translate "remember", "understand", "apply", "analyze", "evaluate", "create"
- Do NOT translate "explanation", "practice", "video", "reading", "interactive"

Return your response in this JSON format:

{{
  "learning_steps": [
    {{
      "title": "Step title",
      "description": "What this step covers and why it's important",
      "topic": "main topic",
      "subtopic": "specific subtopic or null",
      "difficulty_level": "beginner/easy/medium/hard/advanced",
      "learning_objective": "remember/understand/apply/analyze/evaluate/create",
      "content_type": "explanation/practice/video/reading/interactive",
      "content_text": "Specific instructions or content for this step",
      "estimated_duration_minutes": 15-60,
      "addresses_gaps": ["gap_id1", "gap_id2"],
      "prerequisites": ["previous_step_titles"]
    }}
  ],
  "path_rationale": "Why this sequence was chosen",
  "key_progression": "How steps build on each other",
  "expected_outcomes": ["outcome1", "outcome2"]
}}

Generate the learning path now:"""

            # Get AI response with enhanced logging
            logger.info(f"🤖 Sending prompt to AI for learning path generation (language: {language})")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            try:
                response = self.model.generate_content(prompt)
                logger.info(f"✅ AI response received, length: {len(response.text)} characters")
                logger.debug(f"AI response preview: {response.text[:200]}...")
                
                ai_plan = self._parse_ai_learning_plan(response.text)
                logger.info(f"📋 Parsed AI plan with {len(ai_plan.get('learning_steps', []))} steps")
                
            except Exception as e:
                logger.error(f"❌ AI generation failed: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                raise e
            
            # Convert AI response to LearningStep objects
            learning_steps = []
            
            for i, step_data in enumerate(ai_plan.get("learning_steps", [])):
                try:
                    # Handle difficulty level with fallback mapping
                    difficulty_raw = step_data.get("difficulty_level", "medium")
                    difficulty_level = self._map_difficulty_level(difficulty_raw)
                    
                    # Handle learning objective with fallback mapping  
                    objective_raw = step_data.get("learning_objective", "understand")
                    learning_objective = self._map_learning_objective(objective_raw)
                    
                    step = LearningStep(
                        step_id=str(uuid.uuid4()),
                        step_number=i + 1,
                        title=step_data.get("title", f"Learning Step {i + 1}"),
                        description=step_data.get("description", ""),
                        subject=subject,
                        topic=step_data.get("topic", "General"),
                        subtopic=step_data.get("subtopic"),
                        difficulty_level=difficulty_level,
                        learning_objective=learning_objective,
                        content_type=step_data.get("content_type", "explanation"),
                        content_text=step_data.get("content_text", ""),
                        estimated_duration_minutes=step_data.get("estimated_duration_minutes", 20),
                        addresses_gaps=step_data.get("addresses_gaps", []),
                        prerequisites=step_data.get("prerequisites", [])
                    )
                    learning_steps.append(step)
                    
                except Exception as step_error:
                    logger.warning(f"Failed to create step {i+1}: {str(step_error)}")
                    # Continue with next step instead of failing completely
                    continue
            
            # If AI generation fails, create basic steps
            if not learning_steps:
                learning_steps = await self._generate_fallback_learning_steps(
                    knowledge_gaps, subject, grade
                )
            
            return learning_steps
            
        except Exception as e:
            logger.error(f"AI step generation failed, using fallback: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            fallback_steps = await self._generate_fallback_learning_steps(knowledge_gaps, subject, grade)
            logger.info(f"Generated {len(fallback_steps)} fallback steps")
            return fallback_steps
    
    async def _generate_fallback_learning_steps(
        self,
        knowledge_gaps: List[KnowledgeGap],
        subject: str,
        grade: int
    ) -> List[LearningStep]:
        """Generate basic learning steps when AI generation fails."""
        
        steps = []
        
        # Create a step for each knowledge gap
        for i, gap in enumerate(knowledge_gaps[:8]):  # Limit to 8 steps
            step = LearningStep(
                step_id=str(uuid.uuid4()),
                step_number=i + 1,
                title=f"Review {gap.topic}",
                description=f"Strengthen your understanding of {gap.topic} concepts",
                subject=subject,
                topic=gap.topic,
                difficulty_level=gap.difficulty_level,
                learning_objective=gap.learning_objective,
                content_type="practice",
                content_text=f"Practice problems and review concepts related to {gap.topic}",
                estimated_duration_minutes=25,
                addresses_gaps=[gap.gap_id]
            )
            steps.append(step)
        
        return steps
    
    async def get_next_step_for_student(self, student_id: str, path_id: str) -> Optional[Dict[str, Any]]:
        """Get the next learning step for a student, with VIVA integration if applicable."""
        
        try:
            path = await self.get_learning_path(path_id)
            if not path or path.student_id != student_id:
                return None
            
            # Find the next incomplete step
            next_step = None
            for step in path.steps:
                if not step.is_completed:
                    next_step = step
                    break
            
            if not next_step:
                return {"completed": True, "message": "All steps completed!"}
            
            # Prepare step data
            step_data = {
                "step_id": next_step.step_id,
                "title": next_step.title,
                "description": next_step.description,
                "content_type": next_step.content_type,
                "estimated_duration_minutes": next_step.estimated_duration_minutes,
                "has_viva": next_step.content_type == "viva" or getattr(next_step, 'has_viva', False)
            }
            
            # If this step has VIVA, include VIVA readiness info and auto-prepare session
            if step_data["has_viva"]:
                step_data["viva_ready"] = True
                step_data["viva_topic"] = f"{next_step.topic} - {next_step.title}"
                step_data["viva_difficulty"] = next_step.difficulty_level.value
                step_data["viva_objective"] = next_step.learning_objective.value
                
                # Check if there's already an active VIVA session for this step
                if hasattr(next_step, 'viva_session_id') and next_step.viva_session_id:
                    step_data["existing_viva_session"] = next_step.viva_session_id
                else:
                    step_data["needs_viva_session"] = True
            
            return step_data
            
        except Exception as e:
            logger.error(f"Error getting next step for student {student_id}: {str(e)}")
            return None

    async def update_learning_path_progress(
        self,
        path_id: str,
        step_id: str,
        completed: bool,
        performance_score: Optional[float] = None
    ) -> LearningPath:
        """Update progress on a learning path step."""
        
        try:
            # Get current path
            path = await self.get_learning_path(path_id)
            if not path:
                raise ValueError(f"Learning path {path_id} not found")
            
            # Find and update the step
            for step in path.steps:
                if step.step_id == step_id:
                    step.is_completed = completed
                    step.completed_at = datetime.utcnow() if completed else None
                    step.performance_score = performance_score
                    break
            
            # Update path progress
            completed_steps = sum(1 for step in path.steps if step.is_completed)
            path.completion_percentage = (completed_steps / len(path.steps)) * 100 if path.steps else 0
            path.current_step = completed_steps
            path.last_updated = datetime.utcnow()
            
            if path.completion_percentage >= 100:
                path.completed_at = datetime.utcnow()
            
            # Save updated path
            await self._save_learning_path(path)
            
            logger.info(f"Updated progress for path {path_id}: {path.completion_percentage:.1f}% complete")
            return path
            
        except Exception as e:
            logger.error(f"Failed to update learning path progress: {str(e)}")
            raise e
    
    async def get_learning_path(self, path_id: str) -> Optional[LearningPath]:
        """Get a learning path by ID."""
        
        try:
            doc_ref = db.collection(self.learning_paths_collection).document(path_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return LearningPath(**doc.to_dict())
            return None
            
        except Exception as e:
            logger.error(f"Failed to get learning path {path_id}: {str(e)}")
            return None
    
    async def get_student_learning_paths(self, student_id: str) -> List[LearningPath]:
        """Get all learning paths for a student."""
        
        try:
            query = (db.collection(self.learning_paths_collection)
                    .where("student_id", "==", student_id)
                    .order_by("created_at", direction="DESCENDING"))
            
            docs = query.get()
            return [LearningPath(**doc.to_dict()) for doc in docs]
            
        except Exception as e:
            logger.error(f"Failed to get learning paths for student {student_id}: {str(e)}")
            return []
    
    async def adapt_learning_path(
        self,
        path_id: str,
        new_performance_data: StudentPerformance,
        new_gaps: List[KnowledgeGap]
    ) -> LearningPath:
        """Adapt an existing learning path based on new assessment results."""
        
        try:
            path = await self.get_learning_path(path_id)
            if not path:
                raise ValueError(f"Learning path {path_id} not found")
            
            # Analyze if adaptation is needed
            adaptation_needed = await self._assess_adaptation_need(
                path, new_performance_data, new_gaps
            )
            
            if adaptation_needed:
                # Generate new steps for unaddressed gaps
                new_steps = await self._generate_adaptive_steps(
                    path, new_performance_data, new_gaps
                )
                
                # Add new steps to path
                for step in new_steps:
                    step.step_number = len(path.steps) + 1
                    path.steps.append(step)
                
                # Update path metadata
                path.addresses_gaps.extend([gap.gap_id for gap in new_gaps])
                path.total_estimated_duration_minutes += sum(
                    step.estimated_duration_minutes for step in new_steps
                )
                path.last_updated = datetime.utcnow()
                
                # Record adaptation
                adaptation_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "trigger": "new_assessment_results",
                    "changes": f"Added {len(new_steps)} new steps",
                    "new_gaps_addressed": len(new_gaps)
                }
                path.adaptation_history.append(adaptation_record)
                
                # Save adapted path
                await self._save_learning_path(path)
                
                logger.info(f"Adapted learning path {path_id} with {len(new_steps)} new steps")
            
            return path
            
        except Exception as e:
            logger.error(f"Failed to adapt learning path: {str(e)}")
            raise e
    
    # Helper methods
    def _format_knowledge_gaps_for_ai(self, gaps: List[KnowledgeGap]) -> str:
        """Format knowledge gaps for AI prompt."""
        formatted = []
        for gap in gaps:
            formatted.append(
                f"- {gap.topic} ({gap.difficulty_level.value}): "
                f"Severity {gap.severity_score:.2f}, "
                f"Confidence {gap.confidence_score:.2f}, "
                f"Frequency {gap.frequency}"
            )
        return "\\n".join(formatted)
    
    def _parse_ai_learning_plan(self, response_text: str) -> Dict[str, Any]:
        """Parse AI learning plan response with enhanced logging."""
        try:
            import json
            
            logger.debug(f"🔍 Parsing AI response, total length: {len(response_text)}")
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == -1:
                logger.error(f"❌ No JSON found in AI response. Response preview: {response_text[:300]}...")
                return {"learning_steps": []}
            
            json_text = response_text[start_idx:end_idx]
            logger.debug(f"📄 Extracted JSON length: {len(json_text)}")
            logger.debug(f"JSON preview: {json_text[:200]}...")
            
            parsed_data = json.loads(json_text)
            
            # Validate structure
            if "learning_steps" not in parsed_data:
                logger.warning("⚠️ No 'learning_steps' key found in parsed JSON")
                return {"learning_steps": []}
            
            steps_count = len(parsed_data.get("learning_steps", []))
            logger.info(f"✅ Successfully parsed AI plan with {steps_count} learning steps")
            
            # Log first step for validation
            if parsed_data.get("learning_steps"):
                first_step = parsed_data["learning_steps"][0]
                logger.debug(f"First step preview: {first_step.get('title', 'No title')}")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {str(e)}")
            logger.error(f"Problematic JSON: {response_text[max(0, start_idx):min(len(response_text), end_idx)]}")
            return {"learning_steps": []}
        except Exception as e:
            logger.error(f"❌ Unexpected error parsing AI learning plan: {str(e)}")
            logger.error(f"Response type: {type(response_text)}, length: {len(response_text)}")
            return {"learning_steps": []}
    
    def _map_difficulty_level(self, difficulty_raw: str) -> DifficultyLevel:
        """Map AI-generated difficulty level to enum, with strict validation."""
        try:
            # First try direct mapping
            return DifficultyLevel(difficulty_raw.lower())
        except ValueError:
            # Log when AI doesn't follow instructions
            logger.warning(f"⚠️ AI generated non-English difficulty level: '{difficulty_raw}' - This should not happen with proper prompting!")
            
            # Emergency fallback mapping (this should rarely be used)
            difficulty_mapping = {
                # Tamil mappings (emergency fallback only)
                "தொடக்க நிலை": "beginner",
                "எளிய": "easy", 
                "நடுத்தர": "medium",
                "கடினமான": "hard",
                "மேம்பட்ட": "advanced",
                # Telugu mappings (emergency fallback only)
                "ప్రారంభ స్థాయి": "beginner",
                "సులభం": "easy",
                "మధ్యస్థ": "medium", 
                "కష్టం": "hard",
                "అధునాతన": "advanced",
                # Common variations
                "basic": "beginner",
                "simple": "easy",
                "intermediate": "medium",
                "difficult": "hard",
                "expert": "advanced"
            }
            
            mapped_value = difficulty_mapping.get(difficulty_raw.lower(), "medium")
            logger.warning(f"🔧 Emergency mapping: '{difficulty_raw}' → '{mapped_value}'")
            return DifficultyLevel(mapped_value)
    
    def _map_learning_objective(self, objective_raw: str) -> LearningObjectiveType:
        """Map AI-generated learning objective to enum, with strict validation."""
        try:
            # First try direct mapping
            return LearningObjectiveType(objective_raw.lower())
        except ValueError:
            # Log when AI doesn't follow instructions
            logger.warning(f"⚠️ AI generated non-English learning objective: '{objective_raw}' - This should not happen with proper prompting!")
            
            # Emergency fallback mapping (this should rarely be used)
            objective_mapping = {
                # Tamil mappings (emergency fallback only)
                "நினைவில் வைத்துக்கொள்": "remember",
                "புரிந்துகொள்": "understand",
                "பயன்படுத்து": "apply",
                "பகுப்பாய்வு": "analyze",
                "மதிப்பீடு": "evaluate",
                "உருவாக்கு": "create",
                # Telugu mappings (emergency fallback only)
                "గుర్తుంచుకో": "remember",
                "అర్థం చేసుకో": "understand",
                "వర్తింపజేయి": "apply",
                "విశ్లేషించు": "analyze",
                "మూల్యాంకనం": "evaluate",
                "సృష్టించు": "create",
                # Common variations
                "recall": "remember",
                "comprehend": "understand",
                "use": "apply",
                "examine": "analyze",
                "judge": "evaluate",
                "design": "create"
            }
            
            mapped_value = objective_mapping.get(objective_raw.lower(), "understand")
            logger.warning(f"🔧 Emergency mapping: '{objective_raw}' → '{mapped_value}'")
            return LearningObjectiveType(mapped_value)

    def _generate_default_learning_goals(self, gaps: List[KnowledgeGap]) -> List[str]:
        """Generate default learning goals based on knowledge gaps."""
        goals = []
        
        if gaps:
            topics = list(set(gap.topic for gap in gaps))
            goals.extend([f"Master {topic} concepts" for topic in topics[:3]])
            
            if any(gap.severity_score > 0.8 for gap in gaps):
                goals.append("Address critical knowledge gaps")
            
            goals.append("Build confidence in problem-solving")
        
        return goals or ["Improve overall understanding", "Build foundational skills"]
    
    async def _assess_adaptation_need(
        self,
        path: LearningPath,
        new_performance: StudentPerformance,
        new_gaps: List[KnowledgeGap]
    ) -> bool:
        """Assess if learning path needs adaptation."""
        
        # Check for new gaps not addressed by current path
        current_gap_ids = set(path.addresses_gaps)
        new_gap_ids = set(gap.gap_id for gap in new_gaps)
        
        unaddressed_gaps = new_gap_ids - current_gap_ids
        
        # Check for declining performance
        performance_declining = new_performance.score_percentage < 60
        
        return len(unaddressed_gaps) > 0 or performance_declining
    
    async def _generate_adaptive_steps(
        self,
        current_path: LearningPath,
        new_performance: StudentPerformance,
        new_gaps: List[KnowledgeGap]
    ) -> List[LearningStep]:
        """Generate new steps to address newly identified gaps."""
        
        # For now, create simple adaptive steps
        # This could be enhanced with more sophisticated AI analysis
        
        adaptive_steps = []
        
        for gap in new_gaps:
            if gap.gap_id not in current_path.addresses_gaps:
                step = LearningStep(
                    step_id=str(uuid.uuid4()),
                    step_number=0,  # Will be set later
                    title=f"Address {gap.topic} Gap",
                    description=f"Additional practice for {gap.topic} based on recent assessment",
                    subject=current_path.subject,
                    topic=gap.topic,
                    difficulty_level=gap.difficulty_level,
                    learning_objective=gap.learning_objective,
                    content_type="adaptive_practice",
                    content_text=f"Targeted practice to address identified gap in {gap.topic}",
                    estimated_duration_minutes=20,
                    addresses_gaps=[gap.gap_id]
                )
                adaptive_steps.append(step)
        
        return adaptive_steps
    
    async def _save_learning_path(self, path: LearningPath) -> None:
        """Save learning path to Firestore."""
        doc_ref = db.collection(self.learning_paths_collection).document(path.path_id)
        doc_ref.set(path.dict())
    
    async def _generate_lessons_for_steps(self, learning_path: LearningPath) -> None:
        """Generate interactive lessons for each learning step in the path."""
        try:
            # Import here to avoid circular imports
            from app.services.lesson_service import lesson_service
            
            logger.info(f"Generating lessons for {len(learning_path.steps)} learning steps")
            
            for step in learning_path.steps:
                try:
                    # Generate lesson for this step
                    lesson_result = await lesson_service.create_lesson_from_step(
                        learning_step_id=step.step_id,
                        student_id=learning_path.student_id,
                        teacher_uid=learning_path.teacher_uid,
                        customizations={
                            "learning_path_context": {
                                "path_id": learning_path.path_id,
                                "step_number": step.step_number,
                                "total_steps": len(learning_path.steps),
                                "subject": learning_path.subject,
                                "target_grade": learning_path.target_grade
                            }
                        }
                    )
                    
                    if lesson_result.get("success"):
                        # Update step with lesson ID
                        step.content_url = f"/lessons/{lesson_result['lesson_id']}"
                        logger.info(f"Generated lesson {lesson_result['lesson_id']} for step {step.step_id}")
                    else:
                        logger.warning(f"Failed to generate lesson for step {step.step_id}: {lesson_result.get('error')}")
                        
                except Exception as e:
                    logger.error(f"Error generating lesson for step {step.step_id}: {str(e)}")
                    continue
            
            # Update the learning path with lesson URLs
            await self._save_learning_path(learning_path)
            
        except Exception as e:
            logger.error(f"Failed to generate lessons for learning path: {str(e)}")
            # Don't fail the entire path creation if lesson generation fails

# Global instance
learning_path_service = LearningPathService()
