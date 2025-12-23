from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
import uuid
import io
import sys
import os

# Add root to python path so we can import brivas_security
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brivas_security import _verify_image_content, _get_secure_challenge

app = FastAPI(title="Eidolon Liveness API", version="1.0.0")

ACTIVE_CHALLENGES = {}

@app.get("/")
async def root():
    return {"status": "active", "system": "Eidolon 3-Fish Liveness"}

@app.get("/challenge")
async def get_challenge():
    session_id = str(uuid.uuid4())
    prompt_text = _get_secure_challenge()
    user_instruction = prompt_text.replace("a photo of a person ", "")
    ACTIVE_CHALLENGES[session_id] = prompt_text
    print(f"   [SESSION] {session_id} -> {user_instruction}")
    return {"session_id": session_id, "instruction": user_instruction}

@app.post("/verify")
async def verify_liveness(session_id: str = Form(...), file: UploadFile = File(...)):
    target_prompt = ACTIVE_CHALLENGES.get(session_id)
    if not target_prompt:
        raise HTTPException(status_code=400, detail="Invalid or expired session.")
    
    image_bytes = await file.read()
    print(f"   [VERIFYING] Session {session_id} against '{target_prompt}'")
    
    is_valid = _verify_image_content(image_bytes, target_prompt)
    
    # One-time use (Claim 4/5 security)
    del ACTIVE_CHALLENGES[session_id]
    
    if is_valid:
        return {"status": "success", "message": "Biometric Liveness Verified."}
    else:
        raise HTTPException(status_code=401, detail="Liveness Check Failed.")
