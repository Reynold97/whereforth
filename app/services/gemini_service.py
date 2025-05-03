from typing import Dict, Any, Optional
import json
from google import genai
from app.config import settings

class GeminiService:
    """
    Service for interacting with Google's Gemini API.
    Handles basic communication and configuration.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini service with API key"""
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = settings.GEMINI_MODEL
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini
        
        Args:
            prompt (str): The prompt to send to Gemini
            
        Returns:
            str: The generated text
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        
        return response.text
    
    def extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text that might contain markdown, explanations, etc.
        
        Args:
            text (str): The text to extract JSON from
            
        Returns:
            Dict[str, Any]: The extracted JSON as a dictionary
        """
        # Try parsing the whole text as JSON first
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Check for backtick patterns that could be causing issues
            if text.startswith('`') or text.startswith('```'):
                # Handle both single and triple backticks with 'json' label
                if text.startswith('`json'):
                    # Remove the `json prefix
                    clean_text = text[5:].strip()
                    try:
                        return json.loads(clean_text)
                    except:
                        pass
                elif text.startswith('```json'):
                    # Remove the ```json prefix and possible trailing backticks
                    clean_text = text[7:].strip()
                    if clean_text.endswith('```'):
                        clean_text = clean_text[:-3].strip()
                    try:
                        return json.loads(clean_text)
                    except:
                        pass
                elif text.startswith('```'):
                    # Just remove the backticks
                    clean_text = text[3:].strip()
                    if clean_text.endswith('```'):
                        clean_text = clean_text[:-3].strip()
                    try:
                        return json.loads(clean_text)
                    except:
                        pass
                elif text.startswith('`'):
                    # Just remove the single backtick
                    clean_text = text[1:].strip()
                    if clean_text.endswith('`'):
                        clean_text = clean_text[:-1].strip()
                    try:
                        return json.loads(clean_text)
                    except:
                        pass
            
            # First attempt to fix common JSON syntax errors
            text = self._fix_json_syntax(text)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Continue with other extraction methods
                pass
            
            # Look for JSON in code blocks - specifically handling ```json
            if "```json" in text:
                try:
                    # Find the start and end of the JSON code block
                    start = text.find("```json") + 7
                    end = text.find("```", start)
                    if end > start:
                        json_str = text[start:end].strip()
                        return json.loads(json_str)
                except json.JSONDecodeError:
                    # Try to fix the JSON syntax
                    try:
                        json_str = self._fix_json_syntax(text[start:end].strip())
                        return json.loads(json_str)
                    except:
                        pass
            
            # Look for generic code blocks
            if "```" in text:
                parts = text.split("```")
                for i, part in enumerate(parts):
                    # Skip parts that are likely markdown and not code
                    if i % 2 == 0:  # Even parts are outside code blocks
                        continue
                        
                    part = part.strip()
                    # Skip if it starts with a language identifier
                    if part.startswith("json"):
                        part = part[4:].strip()
                        
                    if part and part[0] == "{" and part[-1] == "}":
                        try:
                            return json.loads(part)
                        except:
                            fixed_part = self._fix_json_syntax(part)
                            try:
                                return json.loads(fixed_part)
                            except:
                                continue
            
            # Look for JSON object anywhere in the text
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    json_str = text[start_idx:end_idx]
                    return json.loads(json_str)
                except:
                    # Try to fix the JSON syntax
                    json_str = self._fix_json_syntax(json_str)
                    try:
                        return json.loads(json_str)
                    except:
                        pass
            
            # Last attempt - try to aggressively clean the text
            try:
                cleaned_text = self._aggressively_clean_json(text)
                return json.loads(cleaned_text)
            except:
                pass
                
            # If we still can't find valid JSON, raise an error with details
            raise ValueError(f"Could not extract valid JSON from the response. Original error: {e}. First few chars of text: {text[:500]}...")
    
    def _fix_json_syntax(self, text: str) -> str:
        """
        Attempt to fix common JSON syntax errors
        
        Args:
            text (str): The JSON text to fix
            
        Returns:
            str: The fixed JSON text
        """
        # Replace single quotes with double quotes (but not within already double-quoted strings)
        # This is a simplified approach - a proper parser would be better
        in_string = False
        in_escape = False
        result = []
        
        for char in text:
            if in_escape:
                result.append(char)
                in_escape = False
            elif char == '\\':
                result.append(char)
                in_escape = True
            elif char == '"':
                result.append(char)
                in_string = not in_string
            elif char == "'" and not in_string:
                result.append('"')
            else:
                result.append(char)
        
        fixed_text = ''.join(result)
        
        # Remove trailing commas in objects and arrays
        fixed_text = fixed_text.replace(",\n}", "\n}")
        fixed_text = fixed_text.replace(",\n]", "\n]")
        fixed_text = fixed_text.replace(", }", " }")
        fixed_text = fixed_text.replace(", ]", " ]")
        
        # Fix unquoted property names
        import re
        fixed_text = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', fixed_text)
        
        # Remove JavaScript comments
        lines = fixed_text.split('\n')
        lines = [line for line in lines if not line.strip().startswith('//')]
        fixed_text = '\n'.join(lines)
        
        return fixed_text
    
    def _aggressively_clean_json(self, text: str) -> str:
        """
        Aggressively clean a string to try to extract valid JSON
        
        Args:
            text (str): The text to clean
            
        Returns:
            str: The cleaned text
        """
        # Remove all markdown code block markers
        text = text.replace("```json", "")
        text = text.replace("```", "")
        
        # Ensure the text starts with { and ends with }
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            text = text[start_idx:end_idx]
            
        # Apply syntax fixing
        return self._fix_json_syntax(text)