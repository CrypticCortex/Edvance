#!/usr/bin/env python3

import asyncio
import logging
from app.core.firebase import initialize_firebase
from app.agents.tools.lesson_tools import start_lesson_chat, send_chat_message

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_chatbot_fix():
    """Test if the chatbot fix works."""
    try:
        # Initialize Firebase
        initialize_firebase()
        
        print("🤖 Testing Lesson Chatbot Fix")
        print("=" * 50)
        
        # Start a chat session
        chat_result = await start_lesson_chat(
            lesson_id="test_lesson_123",
            student_id="test_student_456",
            initial_message="Hi, I need help with fractions!"
        )
        
        if not chat_result.get("success"):
            print(f"❌ Failed to start chat: {chat_result.get('error')}")
            return
        
        session_id = chat_result["session_id"]
        print(f"✅ Chat session started: {session_id}")
        
        # Display initial messages
        for msg in chat_result["messages"]:
            sender = "🧑‍🎓 Student" if msg["sender"] == "student" else "🤖 Assistant"
            print(f"   {sender}: {msg['message']}")
        
        print("\n💬 Testing chat response...")
        
        # Send a test message
        response_result = await send_chat_message(
            session_id=session_id,
            student_id="test_student_456",
            message="What exactly is a fraction? I'm confused."
        )
        
        if response_result.get("success"):
            agent_response = response_result["agent_response"]
            print(f"✅ Agent responded successfully!")
            print(f"🤖 Assistant: {agent_response['message']}")
            print(f"💫 Confidence: {agent_response.get('confidence_score', 0)}")
            
            suggested_actions = response_result.get("suggested_actions", [])
            if suggested_actions:
                print(f"💡 Suggestions: {', '.join(suggested_actions)}")
                
            print("\n🎉 CHATBOT FIX SUCCESSFUL!")
        else:
            print(f"❌ Agent failed to respond: {response_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_chatbot_fix())
