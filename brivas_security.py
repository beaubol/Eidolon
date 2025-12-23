import os
import time
import random
import torch
from functools import wraps
from PIL import Image
from dotenv import load_dotenv
from transformers import CLIPProcessor, CLIPModel
import io

load_dotenv()

# We use the standard CLIP model.
MODEL_ID = "openai/clip-vit-base-patch32"

print(">>> [BRIVAS] Initializing Robust Engine...")
try:
    model = CLIPModel.from_pretrained(MODEL_ID)
    processor = CLIPProcessor.from_pretrained(MODEL_ID)
    print(">>> [BRIVAS] Engine Ready.")
except Exception as e:
    print(f">>> [BRIVAS] CRITICAL ERROR: {e}")

class BrivasVerificationError(Exception):
    pass

def _get_secure_challenge():
    """Implements Claim 1(b): Unpredictable prompts"""
    options = ["holding a pen", "holding glasses", "touching their ear"]
    challenge = random.choice(options)
    return f"a photo of a person {challenge}"

def _verify_image_content(image_input, target_prompt):
    """
    Implements Claim 1(d): 
    Accepts file path (str) OR file bytes (stream)
    """
    try:
        # Load image from path or byte stream
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        else:
            image = Image.open(image_input)
        
        # 1. Setup Semantic Battle
        candidate_labels = [target_prompt]
        
        if "pen" in target_prompt:
            candidate_labels.append("a photo of a person holding black glasses")
            candidate_labels.append("a photo of a person holding a cell phone")
        elif "glasses" in target_prompt:
            candidate_labels.append("a photo of a person holding a white pen")
            candidate_labels.append("a photo of a person holding a cell phone")
        else:
            candidate_labels.append("a photo of a person holding a pen")
            candidate_labels.append("a photo of a person holding glasses")
            
        candidate_labels.append("a photo of a person holding nothing")
        
        # 2. Run CLIP
        inputs = processor(text=candidate_labels, images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            
        # 3. Calculate Scores
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        print(f"\n   [BRIVAS SCOREBOARD]")
        for i, label in enumerate(candidate_labels):
            score_pct = probs[i].item() * 100
            marker = "✅" if i == 0 else "❌"
            print(f"   {marker} {score_pct:.1f}% : {label}")
            
        target_score = probs[0].item()
        winner_index = probs.argmax().item()

        if winner_index != 0:
            print(f"   [FAIL] The AI thinks this is '{candidate_labels[winner_index]}'")
            return False
            
        if target_score < 0.90:
            print(f"   [FAIL] Confidence {target_score*100:.1f}% is below threshold (90%)")
            return False
            
        return True

    except Exception as e:
        print(f"   [ERROR] {e}")
        return False