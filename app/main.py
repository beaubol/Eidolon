from fastapi import FastAPI
from app.api.routes import router

# Initialize the Application
app = FastAPI(
    title="Eidolon: Semantic Liveness Backend",
    description="Patent-compliant biometric backend using Zero-Shot ML (CLIP).",
    version="1.0.0"
)

# Connect the 'Traffic Controller' (Routes) we built in Step 3
app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    """
    System Health Check.
    Returns the status of the server.
    """
    return {
        "system": "Eidolon Biometric Backend",
        "status": "ONLINE", 
        "patent_compliance": "ACTIVE",
        "model": "OpenAI CLIP ViT-B/32"
    }

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
