from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .api import endpoints
from .db.init_db import init_db

app = FastAPI(
    title="EcoPrint API",
    description="API for tracking eco-friendly transportation activities",
    version="1.0.0"
)

# Initialize database
init_db()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")

# Include routers
app.include_router(endpoints.router, prefix="/api")
