import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file MUST come before local imports
load_dotenv()

from backend.api.main import app

if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is available
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not set. Orchestrator will fail.")
        
    uvicorn.run(app, host="127.0.0.1", port=8000)
