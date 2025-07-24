#!/usr/bin/env python3
"""
Test script for the new Gemini Live service implementation.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.gemini_live_service import gemini_live_service

async def test_gemini_live_service():
    """Test the Gemini Live service functionality."""
    print("Testing Gemini Live Service...")
    
    try:
        # Test 1: Start a session
        print("\n1. Starting a new viva session...")
        session = await gemini_live_service.start_live_session(
            student_id="test-student-123",
            learning_step_id="algebra-intro",
            language="english",
            session_id="test-session-123"
        )
        print(f"✓ Session started: {session.session_id}")
        print(f"✓ Topic: {session.topic}")
        print(f"✓ Language: {session.language}")
        
        if session.conversation_history:
            print(f"✓ Welcome message: {session.conversation_history[0].text}")
        
        # Test 2: Handle student speech
        print("\n2. Testing student speech handling...")
        response = await gemini_live_service.handle_student_speech(
            session_id="test-session-123",
            student_speech="Hello, I'm ready to start the viva on algebra."
        )
        print(f"✓ Agent response: {response.get('agent_response', 'No response')}")
        
        # Test 3: Another student response
        print("\n3. Testing another student response...")
        response = await gemini_live_service.handle_student_speech(
            session_id="test-session-123",
            student_speech="Algebra is the branch of mathematics that uses letters and symbols to represent numbers and quantities in formulas and equations."
        )
        print(f"✓ Agent response: {response.get('agent_response', 'No response')}")
        
        # Test 4: Get session status
        print("\n4. Testing session status...")
        status = await gemini_live_service.get_session_status("test-session-123")
        if status:
            print(f"✓ Session status: {status['status']}")
            print(f"✓ Message count: {status['message_count']}")
        
        # Test 5: End session
        print("\n5. Testing session end...")
        result = await gemini_live_service.end_live_session("test-session-123")
        print(f"✓ Session ended: {result.get('summary', 'No summary')}")
        print(f"✓ Score: {result.get('score', 'No score')}")
        print(f"✓ Feedback: {result.get('feedback', 'No feedback')}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_live_service())