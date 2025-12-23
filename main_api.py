from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings, Settings
from database.init_db import init_database
from auth.routes import router as auth_router
from reports.routes import router as reports_router
from middleware.rate_limit import rate_limit_middleware


# Create tables automatically on startup
async def lifespan(app: FastAPI):
    # Startup logic
    init_database()
    print("✅ Database tables initialized")

    yield

app = FastAPI(
    title="Financial Report Generator API",
    description="AI-powered financial report generation with user authentication",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(auth_router)
app.include_router(reports_router)

@app.get("/")
def root():
    return {
        "message": "Financial Report Generator API v2.0",
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "me": "GET /auth/me",
                "update_keys": "PUT /auth/api-keys"
            },
            "reports": {
                "generate": "POST /reports/generate",
                "list": "GET /reports/",
                "get_one": "GET /reports/{id}",
                "delete": "DELETE /reports/{id}"
            }
        }
    }

@app.get("/health")
def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_connected": bool(settings.DATABASE_URL),
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)