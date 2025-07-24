# FILE: app/main.py

from fastapi import FastAPI
from app.core.app_factory import create_app
from app.api.v1 import viva as viva_router
from app.core.middleware import configure_middleware

# Create the main app that will handle the WebSocket
app = FastAPI(title="Edvance AI Platform")

# Apply middleware (like CORS) to the main app
configure_middleware(app)

# Include the WebSocket router directly into the main app.
# This ensures its routes are not processed by the ADK's middleware.
app.include_router(viva_router.router)

# Create the ADK-based app which contains all other HTTP routes
adk_app = create_app()

# Mount the entire ADK application. 
# All requests that don't match the Viva router will be passed to this app.
app.mount("/", adk_app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)