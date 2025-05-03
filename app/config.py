import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Simple settings class without using pydantic BaseSettings"""
    
    def __init__(self):
        # API settings
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-04-17")
        
        # App info
        self.APP_NAME = "Whereforth"
        self.APP_VERSION = "0.1.0"
        self.APP_DESCRIPTION = "A tool for generating Period and Cultural Packs (PACs)"
        
        # Data paths
        self.DATA_DIR = "data"
        self.PAC_DIR = "data/pacs"
        
        # Create directories if they don't exist
        os.makedirs(self.PAC_DIR, exist_ok=True)

# Create a singleton instance
settings = Settings()