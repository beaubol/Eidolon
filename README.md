# Eidolon: Semantic Biometric Liveness Backend

**Eidolon** is a next-generation authentication system implementing "Semantic Liveness." It utilizes OpenAI's CLIP architecture to validate user compliance with dynamic, randomized action requests in real-time.

### Core Capabilities
* **Challenge-Response Logic:** Generates random physical challenges (e.g., "Hold a red object," "Touch left ear") to defeat replay attacks.
* **Zero-Shot Verification:** Uses Multimodal AI to mathematically verify video frames against text prompts without specific model retraining.
* **Patent-Compliant:** Implements logic derived from proprietary claims regarding relative movement, contextual verification, and challenge-based authentication.

### Technology Stack
* **Language:** Python 3.10+
* **API Framework:** FastAPI
* **ML Engine:** PyTorch & Transformers (CLIP model)
* **Vision:** Pillow (PIL)

### Deployment
Designed to run in containerized environments or GitHub Codespaces.
