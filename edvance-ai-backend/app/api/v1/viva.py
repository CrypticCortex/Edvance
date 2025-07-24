# FILE: app/api/v1/viva.py

import logging
import asyncio
import json
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status, HTTPException
from app.services.gemini_live_service import gemini_live_service
from app.core.firebase import firebase_auth
from firebase_admin import auth as firebase_auth_errors # Import specific error types

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/viva", tags=["Viva"])

async def stream_audio_responses(websocket: WebSocket, session_id: str):
    """Background task to stream audio responses from Gemini Live API to the client."""
    logger.info(f"Starting audio streaming task for session {session_id}")
    try:
        while True:
            # Get audio data from the service
            audio_data = await gemini_live_service.get_audio_response(session_id)
            if audio_data:
                # Send audio data as base64 encoded JSON message
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                logger.info(f"Sending audio data to client: {len(audio_data)} bytes for session {session_id}")
                await websocket.send_json({
                    "type": "audio_response",
                    "audio": audio_b64,
                    "sample_rate": 24000  # Gemini Live API output sample rate
                })
            else:
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
                
    except asyncio.CancelledError:
        logger.info(f"Audio streaming task cancelled for session {session_id}")
    except Exception as e:
        logger.error(f"Error in audio streaming for session {session_id}: {e}")
        import traceback
        traceback.print_exc()

async def stream_transcription_updates(websocket: WebSocket, session_id: str):
    """Background task to stream transcription updates to the client."""
    logger.info(f"Starting transcription streaming task for session {session_id}")
    try:
        while True:
            # Get transcription update from the service
            transcription_data = await gemini_live_service.get_transcription_update(session_id)
            if transcription_data:
                logger.info(f"Sending transcription to client: {transcription_data['sender']} - {transcription_data['text']}")
                await websocket.send_json(transcription_data)
            else:
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.05)
                
    except asyncio.CancelledError:
        logger.info(f"Transcription streaming task cancelled for session {session_id}")
    except Exception as e:
        logger.error(f"Error in transcription streaming for session {session_id}: {e}")
        import traceback
        traceback.print_exc()

@router.websocket("/{session_id}/speak")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    token: str = Query(...),
    language: str = Query("english"),
    topic: str = Query("algebra")
):
    logger.info(f"WebSocket connection attempt: session_id={session_id}")
    
    # First, accept the connection
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for session {session_id}")
    
    try:
        # Then authenticate the token
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)
        user_id = decoded_token.get('uid')
        logger.info(f"WebSocket connection authenticated for user: {user_id}")
    except firebase_auth_errors.InvalidIdTokenError as e:
        logger.error(f"WebSocket auth failed: Invalid ID Token. Details: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token.")
        return
    except firebase_auth_errors.ExpiredIdTokenError as e:
        logger.error(f"WebSocket auth failed: Expired ID Token. Details: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication token has expired.")
        return
    except firebase_auth_errors.RevokedIdTokenError as e:
        logger.error(f"WebSocket auth failed: Revoked ID Token. Details: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication token has been revoked.")
        return
    except Exception as e:
        logger.error(f"WebSocket auth failed: Unexpected error. Type: {type(e).__name__}, Details: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Could not validate credentials.")
        return
    
    try:
        # Check if session exists, if not create one
        session_status = await gemini_live_service.get_session_status(session_id)
        if not session_status:
            logger.info(f"Creating new Gemini Live session: {session_id}")
            try:
                session = await gemini_live_service.start_live_session(
                    student_id=user_id,
                    learning_step_id=topic,  # Use the topic parameter
                    language=language,  # Use the language parameter
                    session_id=session_id
                )
                
                # Wait a moment for the Live API session to be fully established
                await asyncio.sleep(1.0)
                
                # Send a status message to indicate the session is ready
                await websocket.send_json({
                    "type": "session_ready", 
                    "message": "Live AI session is ready. You can start speaking!",
                    "session_id": session_id
                })
            except Exception as e:
                logger.error(f"Failed to create Gemini Live session: {e}")
                await websocket.send_json({"error": "Failed to initialize AI session", "agent_response": "I'm sorry, there was an error starting our conversation. Please try again."})
                return

        # Start background tasks to stream audio responses and transcriptions
        audio_task = asyncio.create_task(stream_audio_responses(websocket, session_id))
        transcription_task = asyncio.create_task(stream_transcription_updates(websocket, session_id))
        
        while True:
            try:
                # Handle both JSON and binary messages
                message = await websocket.receive()
                
                if "text" in message:
                    # Handle JSON messages (control messages)
                    data = json.loads(message["text"])
                    message_type = data.get("type", "")
                    
                    logger.info(f"Received message type: {message_type}")
                    
                    if message_type == "audio_chunk":
                        # Handle base64 encoded audio data
                        audio_b64 = data.get("audio", "")
                        if audio_b64:
                            try:
                                audio_data = base64.b64decode(audio_b64)
                                logger.info(f"Decoded audio data: {len(audio_data)} bytes")
                                result = await gemini_live_service.handle_audio_input(session_id, audio_data)
                                logger.info(f"Audio input result: {result}")
                            except Exception as e:
                                logger.error(f"Error processing audio chunk: {e}")
                    elif message_type == "text":
                        # Handle text input (fallback)
                        student_speech = data.get("text", "").strip()
                        if student_speech:
                            logger.info(f"Received text input: {student_speech}")
                            response = await gemini_live_service.handle_student_speech(session_id, student_speech)
                            await websocket.send_json(response)
                    elif message_type == "control":
                        # Handle control messages (mute/unmute, etc.)
                        control = data.get("control", "")
                        logger.info(f"Received control: {control}")
                        if control == "mute":
                            await websocket.send_json({"status": "muted", "message": "Audio is muted"})
                        elif control == "unmute":
                            await websocket.send_json({"status": "unmuted", "message": "Audio is active"})
                
                elif "bytes" in message:
                    # Handle raw binary audio data
                    audio_data = message["bytes"]
                    logger.info(f"Received binary audio data: {len(audio_data)} bytes")
                    result = await gemini_live_service.handle_audio_input(session_id, audio_data)
                    logger.info(f"Binary audio input result: {result}")
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                audio_task.cancel()
                transcription_task.cancel()
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message for session {session_id}: {e}")
                await websocket.send_json({"error": str(e), "agent_response": "I'm sorry, I encountered an issue. Could you please try again?"})
                
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        # Clean up session if needed
        try:
            await gemini_live_service.end_live_session(session_id)
        except Exception as e:
            logger.warning(f"Error cleaning up session {session_id}: {e}")

@router.post("/{session_id}/start")
async def start_viva_session(session_id: str, token: str = Query(...)):
    """Start a new viva session."""
    try:
        # Authenticate the token
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)
        user_id = decoded_token.get('uid')
        
        session = await gemini_live_service.start_live_session(
            student_id=user_id,
            learning_step_id="default",
            language="english"
        )
        
        return {
            "session_id": session.session_id,
            "status": "started",
            "message": "Viva session started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting viva session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/end")
async def end_viva_session(session_id: str, token: str = Query(...)):
    """End a viva session and get evaluation."""
    try:
        # Authenticate the token
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)
        
        result = await gemini_live_service.end_live_session(session_id)
        return result
        
    except Exception as e:
        logger.error(f"Error ending viva session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/status")
async def get_session_status(session_id: str, token: str = Query(...)):
    """Get current session status."""
    try:
        # Authenticate the token
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)
        
        status = await gemini_live_service.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))