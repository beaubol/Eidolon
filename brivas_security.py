import os
import time
import random
import torch
from functools import wraps
from PIL import Image
from dotenv import load_dotenv
from transformers import CLIPProcessor, CLIPModel

load_dotenv()
MODEL_ID = "openai/clip-vit-base-patch32"
THRESHOLD = 22.0

try:
    model = CLIPModel.from_pretrained(MODEL_ID)
    processor = CLIPProcessor.from_pretrained(MODEL_ID)
except Exception:
    pass

class BrivasVerificationError(Exception):
    pass

def _get_secure_challenge():
    raw_prompts = os.getenv("BRIVAS_PROMPTS", "holding a pen")
    return f"a photo of a person {random.choice(raw_prompts.split('|'))}"

def _verify_image_content(image_path, prompt_text):
    try:
        image = Image.open(image_path)
        inputs = processor(text=[prompt_text], images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.logits_per_image.item() > THRESHOLD
    except:
        return False

def require_3fish_auth(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        challenge = _get_secure_challenge()
        print(f"\n[BRIVAS] 🔒 Please upload: {challenge}")
        user_image = input(">> Path: ").strip().strip("'").strip('"')
        
        if not os.path.exists(user_image):
             raise BrivasVerificationError("File not found.")
             
        if not _verify_image_content(user_image, challenge):
            print("Access Denied.")
            raise BrivasVerificationError("Liveness Failed.")
            
        print("[BRIVAS] Verified. Executing...")
        return func(self, *args, **kwargs)
    return wrapper
