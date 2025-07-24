# FILE: app/services/gemini_live_service.py

import logging
import asyncio
import json
import base64
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from google import genai
from google.genai import types
from app.core.config import settings
from app.models.viva_models import VivaSession, VivaStatus, VivaMessage

logger = logging.getLogger(__name__)

# Audio configuration matching the example
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
MODEL = "models/gemini-2.5-flash-preview-native-audio-dialog"

class GeminiLiveService:
    """Service to manage Gemini Live sessions for real-time AI interaction with native audio."""

    def __init__(self):
        self.sessions: Dict[str, VivaSession] = {}
        self.live_sessions: Dict[str, Any] = {}  # Store actual live session objects
        self.audio_queues: Dict[str, asyncio.Queue] = {}  # Audio output queues per session
        self.transcription_queues: Dict[str, asyncio.Queue] = {}  # Transcription queues per session
        self._client = None

    @property
    def client(self):
        """Lazy initialization of the GenAI client with v1beta API for Live API."""
        if self._client is None:
            try:
                # Use Developer API with v1beta for Live API access
                api_key = getattr(settings, 'gemini_api_key', None)
                if not api_key:
                    raise ValueError("GEMINI_API_KEY is required for Live API")
                
                self._client = genai.Client(
                    api_key=api_key,
                    http_options=types.HttpOptions(api_version='v1beta')  # v1beta for Live API
                )
                logger.info("Initialized Gemini client with Live API (v1beta)")
                    
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise
                
        return self._client

    def _get_language_name(self, lang_code: str) -> str:
        """Get the full language name from a code."""
        return {"english": "English", "telugu": "Telugu", "tamil": "Tamil"}.get(lang_code, "English")
    
    def _get_topic_name(self, topic_code: str) -> str:
        """Get the full topic name from a code."""
        topics = {
            "algebra": "Introduction to Algebra",
            "geometry": "Basic Geometry", 
            "calculus": "Calculus Fundamentals",
            "physics": "Physics Concepts",
            "chemistry": "Chemistry Basics",
            "biology": "Biology Fundamentals"
        }
        return topics.get(topic_code, "Introduction to Algebra")
    
    def _create_system_instruction(self, topic: str, language: str) -> str:
        """Create language-specific system instruction for the viva."""
        topic_name = self._get_topic_name(topic)
        lang_name = self._get_language_name(language)
        
        if language == "tamil":
            return f"""நீங்கள் ஒரு நட்பான மற்றும் ஊக்கமளிக்கும் AI தேர்வாளர் ஆவீர்கள், வாய்வழி தேர்வு (viva voce) நடத்துகிறீர்கள்.

வழிகாட்டுதல்கள்:
- தலைப்பு: '{topic_name}'
- தேர்வை தமிழில் நடத்துங்கள்
- மாணவர்களின் நிலைக்கு ஏற்ற தெளிவான, சுருக்கமான கேள்விகளைக் கேளுங்கள்
- ஊக்கமளிக்கும் மற்றும் ஆதரவளிக்கும் தன்மையுடன் இருங்கள்
- ஆக்கபூர்வமான கருத்துக்களை வழங்குங்கள்
- உரையாடல் மற்றும் ஈர்க்கக்கூடிய பதில்களை வழங்குங்கள்
- இயல்பான பேச்சு முறைகள் மற்றும் ஒலியேற்றத்தைப் பயன்படுத்துங்கள்
- மாணவர் குழப்பமடைந்தால், குறிப்புகள் வழங்குங்கள் அல்லது கேள்விகளை மறுபரிசீலனை செய்யுங்கள்

மாணவரை அன்புடன் வரவேற்று, {topic_name} பற்றிய viva தொடங்க தயாரா என்று கேட்டு ஆரம்பிக்கவும்."""

        elif language == "telugu":
            return f"""మీరు స్నేహపూర్వకమైన మరియు ప్రోత్సాహకమైన AI పరీక్షకులు, మౌఖిక పరీక్ష (viva voce) నిర్వహిస్తున్నారు.

మార్గదర్శకాలు:
- విషయం: '{topic_name}'
- పరీక్షను తెలుగులో నిర్వహించండి
- విద్యార్థుల స్థాయికి తగిన స్పష్టమైన, సంక్షిప్త ప్రశ్నలు అడగండి
- ప్రోత్సాహకరంగా మరియు మద్దతుగా ఉండండి
- నిర్మాణాత్మక అభిప్రాయాలను అందించండి
- సంభాషణాత్మక మరియు ఆకర్షణీయమైన స్పందనలను ఇవ్వండి
- సహజమైన మాట్లాడే విధానాలు మరియు స్వరాన్ని ఉపయోగించండి
- విద్యార్థి గందరగోళంలో ఉంటే, సూచనలు ఇవ్వండి లేదా ప్రశ్నలను మళ్లీ రూపొందించండి

విద్యార్థిని వెచ్చగా స్వాగతించి, {topic_name} పై viva ప్రారంభించడానికి సిద్ధంగా ఉన్నారా అని అడిగి ప్రారంభించండి."""

        else:  # English
            return f"""You are a friendly and encouraging AI examiner conducting a viva voce (oral exam).
        
Guidelines:
- The topic is '{topic_name}'
- Conduct the viva in {lang_name}
- Ask clear, concise questions appropriate for the student's level
- Be encouraging and supportive
- Provide constructive feedback
- Keep responses conversational and engaging
- Use natural speech patterns and intonation
- If the student seems confused, offer hints or rephrase questions

Start by warmly welcoming the student and asking if they are ready to begin the viva on {topic_name}."""

    def _create_live_config(self, system_instruction: str) -> types.LiveConnectConfig:
        """Create Live API configuration with native audio support and transcription."""
        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],  # Audio only - transcription comes automatically
            media_resolution="MEDIA_RESOLUTION_MEDIUM",
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Zephyr"  # Natural sounding voice
                    )
                )
            ),
            system_instruction=system_instruction,
            generation_config=types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )

    async def start_live_session(self, student_id: str, learning_step_id: str, language: str, session_id: str = None) -> VivaSession:
        """Starts a new Gemini Live session with native audio for viva."""
        if not session_id:
            session_id = f"viva-session-{student_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Use learning_step_id as topic code, fallback to algebra
        topic_code = learning_step_id if learning_step_id != "default" else "algebra"
        topic_name = self._get_topic_name(topic_code)

        # Create session object
        session = VivaSession(
            session_id=session_id,
            student_id=student_id,
            learning_step_id=learning_step_id,
            topic=topic_name,
            language=language,
            status=VivaStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
            conversation_history=[]
        )

        # Create language-specific system instruction
        system_instruction = self._create_system_instruction(topic_code, language)

        try:
            # Create Live API configuration
            config = self._create_live_config(system_instruction)
            
            # Store session objects first
            self.sessions[session_id] = session
            self.audio_queues[session_id] = asyncio.Queue()
            self.transcription_queues[session_id] = asyncio.Queue()
            
            # Start the Live API session management task
            asyncio.create_task(self._manage_live_session(session_id, config))
            
            logger.info(f"Started Gemini Live session with native audio: {session_id} (Language: {language}, Topic: {topic_name})")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start Gemini Live session: {e}")
            raise

    async def _manage_live_session(self, session_id: str, config: types.LiveConnectConfig):
        """Manage the Live API session with proper context manager usage."""
        try:
            async with self.client.aio.live.connect(model=MODEL, config=config) as live_session:
                # Store the live session
                self.live_sessions[session_id] = live_session
                logger.info(f"Live API session connected for {session_id}")
                
                # Send initial greeting to trigger the AI to start speaking
                await live_session.send(input="Hello, I'm ready to start the viva examination.", end_of_turn=True)
                logger.info(f"Sent initial greeting to trigger AI response for {session_id}")
                
                # Start handling responses
                await self._handle_live_responses(session_id, live_session)
                
        except Exception as e:
            logger.error(f"Error in live session management for {session_id}: {e}")
        finally:
            # Clean up when session ends
            self.live_sessions.pop(session_id, None)
            logger.info(f"Live API session ended for {session_id}")

    async def _extract_transcriptions(self, session_id: str, server_content):
        """Extract input and output transcriptions from server content."""
        session = self.sessions.get(session_id)
        if not session:
            return
            
        try:
            logger.info(f"🔍 EXTRACTING TRANSCRIPTIONS - server_content type: {type(server_content)}")
            
            # Debug: Log all attributes of server_content
            if hasattr(server_content, '__dict__'):
                logger.info(f"🔍 SERVER_CONTENT ATTRIBUTES: {list(server_content.__dict__.keys())}")
            
            # Check for input transcription (user speech)
            transcription_fields = ['input_transcription', 'transcription', 'input_text']
            for field in transcription_fields:
                if hasattr(server_content, field):
                    value = getattr(server_content, field)
                    if value:
                        logger.info(f"🎯 USER TRANSCRIPTION FOUND in {field}: {value}")
                        session.conversation_history.append(VivaMessage(sender="student", text=value))
                        await self._send_transcription_update(session_id, "student", value)
                        break
            
            # Check for output transcription (AI speech)
            output_fields = ['output_transcription', 'text', 'output_text']
            for field in output_fields:
                if hasattr(server_content, field):
                    value = getattr(server_content, field)
                    if value:
                        logger.info(f"🎯 AI TRANSCRIPTION FOUND in {field}: {value}")
                        session.conversation_history.append(VivaMessage(sender="agent", text=value))
                        await self._send_transcription_update(session_id, "agent", value)
                        break
            
            # Check model_turn for transcription data
            if hasattr(server_content, 'model_turn') and server_content.model_turn:
                model_turn = server_content.model_turn
                logger.info(f"🔍 MODEL_TURN found, checking for transcriptions...")
                
                if hasattr(model_turn, '__dict__'):
                    logger.info(f"🔍 MODEL_TURN ATTRIBUTES: {list(model_turn.__dict__.keys())}")
                
                # Check for text in model_turn parts
                if hasattr(model_turn, 'parts') and model_turn.parts:
                    for i, part in enumerate(model_turn.parts):
                        logger.info(f"🔍 PART {i} type: {type(part)}")
                        if hasattr(part, '__dict__'):
                            logger.info(f"🔍 PART {i} ATTRIBUTES: {list(part.__dict__.keys())}")
                        
                        if hasattr(part, 'text') and part.text:
                            logger.info(f"🎯 PART TEXT TRANSCRIPTION FOUND: {part.text}")
                            session.conversation_history.append(VivaMessage(sender="agent", text=part.text))
                            await self._send_transcription_update(session_id, "agent", part.text)
                            break
                
        except Exception as e:
            logger.error(f"Error extracting transcriptions for session {session_id}: {e}")
            import traceback
            traceback.print_exc()

    async def _send_transcription_update(self, session_id: str, sender: str, text: str):
        """Send transcription update to WebSocket clients."""
        # Store transcription update in a queue for WebSocket delivery
        transcription_queue = getattr(self, 'transcription_queues', {}).get(session_id)
        if transcription_queue:
            try:
                await transcription_queue.put({
                    "type": "transcription",
                    "sender": sender,
                    "text": text,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Error sending transcription update: {e}")

    async def _handle_live_responses(self, session_id: str, live_session):
        """Background task to handle responses from the Live API session."""
        session = self.sessions.get(session_id)
        audio_queue = self.audio_queues.get(session_id)
        
        if not session or not audio_queue:
            logger.error(f"Missing session components for {session_id}")
            return
            
        try:
            logger.info(f"Starting response handler for session {session_id}")
            while True:
                logger.debug(f"Waiting for response from Live API for session {session_id}")
                turn = live_session.receive()
                logger.info(f"Received turn from Live API for session {session_id}")
                
                async for response in turn:
                    logger.info(f"Processing response: {type(response)} for session {session_id}")
                    
                    # Debug: Check if response has text attribute
                    if hasattr(response, 'text'):
                        if response.text:
                            logger.info(f"🔍 Response has text attribute: '{response.text}'")
                        else:
                            logger.info(f"🔍 Response has text attribute but it's empty/None")
                    else:
                        logger.info(f"🔍 Response does NOT have text attribute")
                    
                    # Debug: Check if response has data attribute
                    if hasattr(response, 'data'):
                        if response.data:
                            logger.info(f"🔍 Response has data attribute: {len(response.data)} bytes")
                        else:
                            logger.info(f"🔍 Response has data attribute but it's empty/None")
                    else:
                        logger.info(f"🔍 Response does NOT have data attribute")
                    
                    # Flag to track if we've processed audio for this response
                    audio_processed = False
                    text_processed = False
                    
                    # Primary method: Check server_content for model_turn with parts
                    if hasattr(response, 'server_content') and response.server_content:
                        server_content = response.server_content
                        logger.info(f"Server content type: {type(server_content)}")
                        
                        # Extract transcriptions from server_content
                        await self._extract_transcriptions(session_id, server_content)
                        
                        if hasattr(server_content, 'model_turn') and server_content.model_turn:
                            model_turn = server_content.model_turn
                            if hasattr(model_turn, 'parts') and model_turn.parts:
                                for part in model_turn.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data and not audio_processed:
                                        if hasattr(part.inline_data, 'data') and part.inline_data.data:
                                            logger.info(f"Received audio data: {len(part.inline_data.data)} bytes for session {session_id}")
                                            await audio_queue.put(part.inline_data.data)
                                            audio_processed = True
                                    elif hasattr(part, 'text') and part.text and not text_processed:
                                        logger.info(f"AI response text: {part.text}")
                                        session.conversation_history.append(
                                            VivaMessage(sender="agent", text=part.text)
                                        )
                                        text_processed = True
                    
                    # Skip further processing if we already found audio/text
                    if audio_processed or text_processed:
                        continue
                    
                    # Fallback 1: Check direct attributes (only if not already processed)
                    if hasattr(response, 'data') and response.data and not audio_processed:
                        logger.info(f"Received audio data (direct): {len(response.data)} bytes for session {session_id}")
                        await audio_queue.put(response.data)
                        audio_processed = True
                        continue
                    
                    if hasattr(response, 'text') and response.text and not text_processed:
                        logger.info(f"🎯 TRANSCRIPTION FOUND - AI response text (direct): {response.text}")
                        session.conversation_history.append(
                            VivaMessage(sender="agent", text=response.text)
                        )
                        # Send transcription update via WebSocket
                        await self._send_transcription_update(session_id, "agent", response.text)
                        text_processed = True
                        continue
                    
                    # Skip model_dump processing if we already processed audio/text
                    if audio_processed or text_processed:
                        continue
                    
                    # Fallback 2: Try model_dump() only if nothing processed yet
                    if hasattr(response, 'model_dump'):
                        try:
                            response_data = response.model_dump()
                            logger.info(f"Response model_dump: {response_data}")
                            
                            # Look for audio data in the dumped structure
                            if 'server_content' in response_data and not audio_processed:
                                server_content = response_data['server_content']
                                if server_content and 'model_turn' in server_content:
                                    model_turn = server_content['model_turn']
                                    if model_turn and 'parts' in model_turn:
                                        for part in model_turn['parts']:
                                            if 'inline_data' in part and part['inline_data'] and not audio_processed:
                                                inline_data = part['inline_data']
                                                if 'data' in inline_data and inline_data['data']:
                                                    # Found audio data!
                                                    audio_data = base64.b64decode(inline_data['data'])
                                                    logger.info(f"Found audio data in model_dump: {len(audio_data)} bytes for session {session_id}")
                                                    await audio_queue.put(audio_data)
                                                    audio_processed = True
                                                    break
                                            elif 'text' in part and part['text'] and not text_processed:
                                                logger.info(f"Found text in model_dump: {part['text']}")
                                                session.conversation_history.append(
                                                    VivaMessage(sender="agent", text=part['text'])
                                                )
                                                text_processed = True
                                                break
                        except Exception as e:
                            logger.error(f"Error processing model_dump: {e}")
                    
                    # Enhanced debugging: Check if this is an audio response based on usage metadata
                    if not audio_processed and not text_processed:
                        # Check usage metadata for audio tokens
                        if hasattr(response, 'usage_metadata') and response.usage_metadata:
                            usage = response.usage_metadata
                            if hasattr(usage, 'response_tokens_details') and usage.response_tokens_details:
                                for token_detail in usage.response_tokens_details:
                                    if hasattr(token_detail, 'modality') and str(token_detail.modality) == "MediaModality.AUDIO":
                                        logger.warning(f"Audio tokens detected ({token_detail.token_count}) but no audio data found for session {session_id}")
                                        
                                        # Try to find audio data in different locations
                                        logger.info(f"Searching for audio data in response object...")
                                        
                                        # Check if response has 'data' attribute directly
                                        if hasattr(response, 'data'):
                                            logger.info(f"Response.data type: {type(response.data)}, value: {response.data}")
                                        
                                        # Check all attributes of the response
                                        for attr_name in dir(response):
                                            if not attr_name.startswith('_'):
                                                try:
                                                    attr_value = getattr(response, attr_name)
                                                    if attr_value is not None and not callable(attr_value):
                                                        logger.info(f"Response.{attr_name}: {type(attr_value)} = {attr_value}")
                                                        
                                                        # Check if this attribute contains audio data
                                                        if isinstance(attr_value, bytes) and len(attr_value) > 0:
                                                            logger.info(f"Found bytes data in {attr_name}: {len(attr_value)} bytes")
                                                            await audio_queue.put(attr_value)
                                                            audio_processed = True
                                                            break
                                                except Exception as e:
                                                    logger.debug(f"Error accessing {attr_name}: {e}")
                                        
                                        if audio_processed:
                                            break
                        
                        if not audio_processed and not text_processed:
                            logger.debug(f"No audio or text found in response for session {session_id}")
                        
        except Exception as e:
            logger.error(f"Error in live response handler for session {session_id}: {e}")
            import traceback
            traceback.print_exc()



    async def get_audio_response(self, session_id: str) -> Optional[bytes]:
        """Get audio response data from the queue."""
        audio_queue = self.audio_queues.get(session_id)
        if not audio_queue:
            return None
            
        try:
            # Wait for audio data with timeout
            audio_data = await asyncio.wait_for(audio_queue.get(), timeout=1.0)
            return audio_data
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error getting audio response for session {session_id}: {e}")
            return None

    async def get_transcription_update(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get transcription update from the queue."""
        transcription_queue = self.transcription_queues.get(session_id)
        if not transcription_queue:
            return None
            
        try:
            # Wait for transcription data with short timeout
            transcription_data = await asyncio.wait_for(transcription_queue.get(), timeout=0.1)
            return transcription_data
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error getting transcription update for session {session_id}: {e}")
            return None

    async def handle_audio_input(self, session_id: str, audio_data: bytes) -> Dict[str, Any]:
        """Handle audio input from the student using Live API."""
        live_session = self.live_sessions.get(session_id)
        session = self.sessions.get(session_id)
        
        if not live_session or not session:
            return {"error": "Session not found"}
            
        try:
            # Send audio data to Live API
            await live_session.send(input={
                "data": audio_data,
                "mime_type": "audio/pcm"
            })
            
            return {"status": "audio_sent"}
            
        except Exception as e:
            logger.error(f"Error handling audio input for session {session_id}: {e}")
            return {"error": str(e)}

    async def handle_student_speech(self, session_id: str, student_speech: str) -> Dict[str, Any]:
        """Handles student speech through Gemini Live API (fallback for text input)."""
        live_session = self.live_sessions.get(session_id)
        session = self.sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found", "agent_response": "Session not found."}

        try:
            # Add student message to conversation history
            session.conversation_history.append(VivaMessage(sender="student", text=student_speech))

            if live_session:
                # Send text to Live API session
                await live_session.send(input=student_speech, end_of_turn=True)
                return {"status": "text_sent_to_live_api"}
            else:
                # Fallback to regular content generation if Live API session not available
                history_str = "\n".join([f"{msg.sender}: {msg.text}" for msg in session.conversation_history])
                lang_name = self._get_language_name(session.language)
                
                prompt = f"""You are an AI examiner conducting a viva in {lang_name} on the topic '{session.topic}'.
                
Below is the conversation history. The student has just spoken. 
Your task is to evaluate their response and ask the next logical question or provide feedback.
Keep your responses clear, concise, and encouraging.

Conversation History:
{history_str}

Provide your next response as the examiner:"""

                response = await self.client.aio.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents=prompt
                )
                
                response_text = response.text if response.text else "I'm sorry, I didn't catch that. Could you please repeat your answer?"
                session.conversation_history.append(VivaMessage(sender="agent", text=response_text))
                
                return {"agent_response": response_text}
            
        except Exception as e:
            logger.error(f"Error handling student speech in session {session_id}: {e}")
            return {"error": str(e), "agent_response": "I'm sorry, I encountered an issue. Could you please repeat your answer?"}

    async def end_live_session(self, session_id: str) -> Dict[str, Any]:
        """Ends a Gemini session and generates final evaluation."""
        session = self.sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found", "summary": "Session not found."}

        try:
            # Generate final evaluation using the conversation history
            history_str = "\n".join([f"{msg.sender}: {msg.text}" for msg in session.conversation_history])
            lang_name = self._get_language_name(session.language)

            evaluation_prompt = f"""Based on this viva conversation in {lang_name} on '{session.topic}', provide a final evaluation.

Conversation History:
{history_str}

Provide a JSON response with:
- "score": integer from 0-100
- "feedback": constructive feedback string
- "strengths": list of student's strengths
- "areas_for_improvement": list of areas to improve

Respond ONLY with valid JSON."""

            # Use regular generate_content for evaluation
            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=evaluation_prompt
            )
            
            # Parse evaluation response
            try:
                cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
                result = json.loads(cleaned_response)
                score = result.get("score", 0)
                feedback = result.get("feedback", "No feedback generated.")
                strengths = result.get("strengths", [])
                areas_for_improvement = result.get("areas_for_improvement", [])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse evaluation JSON: {e}")
                score = 0
                feedback = "Could not generate evaluation. Please review manually."
                strengths = []
                areas_for_improvement = []

            # Update session
            session.status = VivaStatus.COMPLETED
            session.ended_at = datetime.utcnow()
            session.score = score
            session.feedback = feedback

            # Clean up Live API session and resources
            live_session = self.live_sessions.get(session_id)
            if live_session:
                try:
                    await live_session.close()
                    logger.info(f"Closed Live API session for {session_id}")
                except Exception as e:
                    logger.warning(f"Error closing Live API session {session_id}: {e}")

            # Clean up all session data
            self.sessions.pop(session_id, None)
            self.live_sessions.pop(session_id, None)
            self.audio_queues.pop(session_id, None)
            self.transcription_queues.pop(session_id, None)

            return {
                "summary": "Viva completed successfully!",
                "score": score,
                "feedback": feedback,
                "strengths": strengths,
                "areas_for_improvement": areas_for_improvement
            }
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return {"error": str(e), "summary": "Error completing viva evaluation."}

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a live session."""
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        return {
            "session_id": session.session_id,
            "student_id": session.student_id,
            "topic": session.topic,
            "language": session.language,
            "status": session.status.value,
            "started_at": session.started_at.isoformat(),
            "message_count": len(session.conversation_history)
        }

# Global instance
gemini_live_service = GeminiLiveService()