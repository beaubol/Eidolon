import os
import time
import random
import torch
from functools import wraps
from PIL import Image
from dotenv import load_dotenv
from transformers import CLIPProcessor, CLIPModel

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
    # These must match the logic in verification below
    # We support 'pen' and 'glasses' specifically for this test
    options = ["holding a pen", "holding glasses", "touching their ear"]
    challenge = random.choice(options)
    return f"a photo of a person {challenge}"

def _verify_image_content(image_path, target_prompt):
    """
    Implements Claim 1(d):
    Uses CONTRASTIVE assessment. We compare the image against 
    the target prompt AND several "wrong" prompts.
    """
    try:
        image = Image.open(image_path)
        
        # 1. Setup Semantic Battle
        candidate_labels = [target_prompt] # Index 0 is always the RIGHT answer
        
        # Add hard negatives (Distractors) based on the target
        if "pen" in target_prompt:
            candidate_labels.append("a photo of a person holding black glasses")
            candidate_labels.append("a photo of a person holding a cell phone")
        elif "glasses" in target_prompt:
            candidate_labels.append("a photo of a person holding a white pen")
            candidate_labels.append("a photo of a person holding a cell phone")
        else:
            # Fallback distractors for "touching ear" etc.
            candidate_labels.append("a photo of a person holding a pen")
            candidate_labels.append("a photo of a person holding glasses")
            
        candidate_labels.append("a photo of a person holding nothing")
        
        # 2. Process inputs
        inputs = processor(text=candidate_labels, images=image, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            outputs = model(**inputs)
            
        # 3. Calculate Probabilities (Softmax)
        # logits_per_image is the similarity score
        probs = outputs.logits_per_image.softmax(dim=1)[0] # Get percentages
        
        # 4. Print the Scoreboard (Debugging)
        print(f"\n   [BRIVAS SCOREBOARD]")
        for i, label in enumerate(candidate_labels):
            score_pct = probs[i].item() * 100
            marker = "✅" if i == 0 else "❌"
            print(f"   {marker} {score_pct:.1f}% : {label}")
            
        target_score = probs[0].item()
        winner_index = probs.argmax().item()

        # 5. STRICT RULES
        # Rule A: The target must be the winner.
        if winner_index != 0:
            print(f"   [FAIL] The AI thinks this is '{candidate_labels[winner_index]}'")
            return False
            
        # Rule B: The confidence must be > 90% (Strict Liveness)
        if target_score < 0.90:
            print(f"   [FAIL] Confidence {target_score*100:.1f}% is below threshold (90%)")
            return False
            
        return True

    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def require_3fish_auth(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        challenge = _get_secure_challenge()
        print(f"\n[BRIVAS] 🔒 Please upload: {challenge}")
        
        # Loop for CLI usability
        while True:
            user_image = input(">> Path (or 'q' to quit): ").strip().strip("'").strip('"')
            if user_image.lower() == 'q': return
            if os.path.exists(user_image):
                break
            print("   [!] File not found. Try again.")

        if not _verify_image_content(user_image, challenge):
            print("   [ACCESS DENIED] Image matches a different object or confidence too low.")
            raise BrivasVerificationError("Liveness Failed.")
            
        print("[BRIVAS] Verified. Executing...")
        return func(self, *args, **kwargs)
    return wrapper