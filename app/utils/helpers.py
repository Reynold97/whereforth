import json
import os
from datetime import datetime
from typing import List, Optional
from app.schemas.simple_pac_schemas import SimplePAC
from app.config import settings

def save_pac_to_file(pac: SimplePAC, filename: Optional[str] = None) -> str:
    """
    Save a PAC to a JSON file
    
    Args:
        pac (SimplePAC): The PAC to save
        filename (str, optional): The filename to save to. If None, a filename will be generated.
        
    Returns:
        str: The path to the saved file
    """
    if filename is None:
        # Generate a filename from the PAC metadata
        title = pac.pac_metadata.title.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.json"
    
    # Ensure the directory exists
    os.makedirs(settings.PAC_DIR, exist_ok=True)
    
    # Full path
    filepath = os.path.join(settings.PAC_DIR, filename)
    
    # Save as JSON
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(pac.model_dump_json(indent=2))
    
    return filepath

def load_pac_from_file(filepath: str) -> SimplePAC:
    """
    Load a PAC from a JSON file
    
    Args:
        filepath (str): The path to the JSON file
        
    Returns:
        SimplePAC: The loaded PAC
    """
    with open(filepath, "r", encoding="utf-8") as f:
        pac_data = json.load(f)
    
    return SimplePAC.model_validate(pac_data)

def list_available_pacs() -> List[str]:
    """
    List all available PACs
    
    Returns:
        list: A list of PAC filenames
    """
    if not os.path.exists(settings.PAC_DIR):
        return []
    
    return [f for f in os.listdir(settings.PAC_DIR) if f.endswith(".json")]

def get_pac_details(filename: str) -> dict:
    """
    Get basic details about a PAC without loading the entire file
    
    Args:
        filename (str): The filename of the PAC
        
    Returns:
        dict: Basic details about the PAC
    """
    filepath = os.path.join(settings.PAC_DIR, filename)
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    # Extract just the metadata
    if "pac_metadata" in data:
        return data["pac_metadata"]
    
    return {
        "title": filename.replace(".json", "").replace("_", " ").title(),
        "period": "Unknown",
        "regions": [],
        "description": "No metadata available"
    }