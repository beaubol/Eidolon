from PIL import Image
import io
import torch
from transformers import CLIPProcessor, CLIPModel

class LivenessEngine:
    def __init__(self):
        """
        Initializes the CLIP model.
        This is the 'Sophisticated ML Construct' that understands both 
        images and text (Semantic Liveness).
        """
        self.model_id = "openai/clip-vit-base-patch32"
        print(f"Initializing Liveness Brain: {self.model_id}...")
        
        # Load model and processor from Hugging Face (Free/Open Source)
        self.model = CLIPModel.from_pretrained(self.model_id)
        self.processor = CLIPProcessor.from_pretrained(self.model_id)
        print("Liveness Brain Ready.")

    def verify_action(self, image_bytes: bytes, action_request: str) -> dict:
        """
        Verifies if the image matches the Action Request (Claim 1).
        
        Args:
            image_bytes: The raw image data from the user's camera.
            action_request: The specific instruction (e.g., "User holding a red light").
            
        Returns:
            Dictionary containing the probability score and boolean result.
        """
        try:
            # 1. Convert bytes to an image
            image = Image.open(io.BytesIO(image_bytes))

            # 2. Create a comparison set: 
            # We compare the Action Request vs. a generic "User doing nothing" 
            # to see which one the AI thinks is more accurate.
            labels = [action_request, "A photo of a user doing nothing"]

            # 3. Process inputs through the ML Construct
            inputs = self.processor(text=labels, images=image, return_tensors="pt", padding=True)

            # 4. Forward pass (The AI analyzes the semantic content)
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image  # Similarity score
            probs = logits_per_image.softmax(dim=1)      # Convert to probability %

            # 5. Extract the score for the requested action (index 0)
            confidence_score = probs[0][0].item()
            
            # Threshold: We require 85% confidence to pass authentication
            is_live = confidence_score > 0.85

            return {
                "is_verified": is_live,
                "confidence": round(confidence_score * 100, 2),
                "analyzed_action": action_request
            }

        except Exception as e:
            print(f"Error in LivenessEngine: {str(e)}")
            return {"is_verified": False, "error": str(e)}

# Create a global instance to be used by the API
engine = LivenessEngine()
