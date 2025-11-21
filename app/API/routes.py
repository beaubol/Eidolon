from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.vision import engine
import random
from typing import Optional

router = APIRouter()

# Claim 1: "plurality of predefined acts"
# These map to Claims 2 (Colors), Claim 4 (Gestures), and Claim 5 (Angles)
PREDEFINED_ACTS = [
    "User holding a red object",             # Claim 2
    "User touching their left ear",          # Claim 4
    "User covering their right eye",         # Claim 4
    "User illuminating a blue light",        # Claim 2
    "User looking up and to the left",       # Claim 5 (Angle)
    "User holding a phone with a flash on"   # Claim 3
]

@router.get("/challenge")
async def get_challenge():
    """
    Claim 1 Step: "selecting a predefined act from a plurality of predefined acts"
    
    The server selects a random challenge and sends it to the user.
    This prevents the user from knowing the challenge in advance.
    """
    selected_act = random.choice(PREDEFINED_ACTS)
    
    # Claim 1 Step: "providing an action request to said particular user"
    return {
        "challenge_id": random.randint(1000, 9999),
        "action_request": selected_act,
        "instructions": f"Please record yourself: {selected_act}"
    }

@router.post("/verify")
async def verify_user(
    image: UploadFile = File(...),           # Claim 1: "receiving a recording"
    action_request: str = Form(...),         # The challenge they are responding to
    context_data: Optional[str] = Form(None) # Claim 1 & 8: "receiving contextual data"
):
    """
    Claim 1 Step: "determining whether said recording indicates a live performance"
    """
    print(f"Received verification request for challenge: {action_request}")
    
    if not action_request:
        raise HTTPException(status_code=400, detail="Action request context missing")

    # Read the uploaded image file
    image_bytes = await image.read()
    
    # Pass data to the 'Sophisticated ML Construct' (Our CLIP Engine)
    # This executes the comparison between the Image and the Text
    result = engine.verify_action(image_bytes, action_request)
    
    # Claim 1 Step: "authenticating... if said recording indicates a live performance"
    if result["is_verified"]:
        return {
            "status": "ACCESS_GRANTED", # Claim 12: Providing access to resource
            "verification_details": result,
            "message": "Liveness confirmed. Identity Verified."
        }
    else:
        return {
            "status": "ACCESS_DENIED",
            "verification_details": result,
            "message": "Liveness check failed. Action did not match request."
        }
