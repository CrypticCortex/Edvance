# FILE: app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.firebase import initialize_firebase

# Initialize Firebase Admin SDK on startup
initialize_firebase()

# Create the FastAPI app instance
app = FastAPI(
    title="Edvance AI Teaching Assistant API",
    description="Backend services for the Edvance AI application.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],

    allow_headers=["*"],
)


@app.get("/", tags=["Health Check"])
def read_root():
    """
    A simple health check endpoint to confirm the API is running.
    """
    return {"status": "ok", "message": "Welcome to the Edvance AI API!"}


# === ADD THIS PART ===
# Include API routers
from app.api.v1 import auth as auth_router

# Add the authentication router to the main application
app.include_router(auth_router.router, prefix="/v1/auth", tags=["Authentication"])