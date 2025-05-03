from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging

from google import genai
from app.schemas.simple_pac_schemas import SimplePAC, PACMetadata, PAC_TEMPLATE
from app.config import settings

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini service with API key"""
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = settings.GEMINI_MODEL
    
    def generate_pac(self, culture: str, time_period: str, detailed: bool = False, max_retries: int = 3) -> SimplePAC:
        """
        Generate a Period and Cultural Pack (PAC) for the specified culture and time period
        
        Args:
            culture (str): The culture to generate a PAC for (e.g., "Viking Age Scandinavia")
            time_period (str): The time period (e.g., "793-1066 CE")
            detailed (bool): Whether to generate a detailed PAC
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            SimplePAC: A structured PAC object
        """
        # Create metadata
        metadata = PACMetadata(
            title=f"{culture}",
            period=time_period,
            regions=[],  # Will be populated by Gemini
            description="",  # Will be populated by Gemini
            created_at=datetime.now().isoformat(),
            source="Gemini",
            version="0.1.0",
            tags=[]
        )
        
        # Implement retry mechanism
        errors = []
        for attempt in range(max_retries):
            try:
                # Create prompt (slightly different each time to encourage variation)
                prompt = self._create_pac_prompt(culture, time_period, detailed, attempt)
                
                # Use a simple text-based approach without the schema
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                # Try to parse JSON from the response
                response_text = response.text
                
                # Extract JSON from the text
                json_data = self._extract_json_from_text(response_text)
                
                # Ensure metadata fields are properly set
                if "pac_metadata" in json_data:
                    json_data["pac_metadata"]["created_at"] = metadata.created_at
                    json_data["pac_metadata"]["source"] = metadata.source
                    json_data["pac_metadata"]["version"] = metadata.version
                else:
                    json_data["pac_metadata"] = metadata.model_dump()
                
                # Create PAC object
                pac = SimplePAC.model_validate(json_data)
                return pac
                
            except Exception as e:
                errors.append(f"Attempt {attempt+1} failed: {str(e)}")
                # If this isn't the last attempt, continue to the next one
                if attempt < max_retries - 1:
                    continue
                
                # If all attempts fail, raise the error with details about each attempt
                error_details = "\n".join(errors)
                raise ValueError(f"All {max_retries} attempts failed to generate PAC:\n{error_details}")

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
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
    
    def _create_pac_prompt(self, culture: str, time_period: str, detailed: bool = False, attempt: int = 0) -> str:
        """
        Create a prompt for Gemini to generate a PAC
        
        Args:
            culture (str): The culture to generate a PAC for
            time_period (str): The time period
            detailed (bool): Whether to generate a detailed PAC
            attempt (int): The current attempt number
            
        Returns:
            str: The prompt
        """
        # Build a detailed prompt from the PAC_TEMPLATE
        sections_text = ""
        for section in PAC_TEMPLATE["sections"]:
            sections_text += f"\n## {section['name'].title()}: {section['description']}\n"
            
            for subsection in section["subsections"]:
                sections_text += f"\n### {subsection['name'].title()}: {subsection['description']}\n"
                
                for detail in subsection["required_details"]:
                    sections_text += f"- {detail}\n"
        
        detail_level = "detailed and comprehensive" if detailed else "concise but informative"
        
        # Add some variability based on attempt number to encourage different responses
        emphasis = ["", "IMPORTANT: ", "CRITICAL: "][min(attempt, 2)]
        style_note = [
            "",
            " Do not use markdown code blocks.",
            " Provide raw JSON only without any markdown formatting."
        ][min(attempt, 2)]
        
        # Create a comprehensive example to guide the structure
        example_json = """
{
  "pac_metadata": {
    "title": "Viking Age Scandinavia",
    "period": "793-1066 CE",
    "regions": ["Norway", "Denmark", "Sweden", "Iceland"],
    "tags": ["Vikings", "Norse", "Medieval", "Scandinavia"],
    "description": "The Viking Age was a period during the Middle Ages when Norsemen known as Vikings undertook large-scale raiding, colonizing, conquest, and trading throughout Europe and reached North America."
  },
  "visual_elements": {
    "architecture": {
      "dwellings": {
        "description": "Viking homes varied by region and status",
        "key_features": ["Longhouses with central hearths", "Turf roofs for insulation"]
      },
      "religious_structures": {
        "description": "Sacred spaces for worship of Norse gods",
        "key_features": ["Open air ritual sites", "Temple buildings (hofs)"]
      }
    },
    "clothing": {
      "male": {
        "everyday": {
          "description": "Practical garments suited for cold climate",
          "items": ["Woolen tunic", "Linen undershirt", "Trousers"],
          "materials": ["Wool", "Linen", "Leather"]
        }
      },
      "female": {
        "everyday": {
          "description": "Layered clothing for warmth and mobility",
          "items": ["Underdress (serk)", "Hangerock (pinafore dress)", "Brooches"],
          "materials": ["Wool", "Linen", "Hemp"]
        }
      }
    },
    "artifacts": {
      "weapons": {
        "swords": {
          "description": "High-status weapons with pattern-welded blades",
          "key_features": ["Pattern-welded steel", "Decorated hilts"]
        },
        "axes": ["Bearded axes", "Danish axes"]
      },
      "tools": ["Farming implements", "Shipbuilding tools", "Textile equipment"]
    },
    "art_motifs": {
      "styles": {
        "oseberg": {
          "period": "Early Viking Age",
          "characteristics": ["Gripping beasts", "Interlace patterns"]
        }
      },
      "common_symbols": ["Dragons", "Ravens", "Wolves", "Ships"]
    },
    "color_palette": {
      "common": ["Red", "Blue", "Yellow", "Green", "Brown"],
      "dyes": {
        "sources": ["Woad (blue)", "Madder (red)", "Weld (yellow)"]
      }
    }
  },
  "cultural_behaviors": {
    "social_structure": {
      "classes": ["Jarls (nobles)", "Karls (free farmers)", "Thralls (slaves)"],
      "leadership": "Chieftains and kings ruled through a combination of wealth, military prowess, and perceived divine favor"
    },
    "daily_life": {
      "food": ["Bread", "Porridge", "Dairy products", "Fish", "Game", "Preserved meats"],
      "occupations": ["Farming", "Fishing", "Crafting", "Trading", "Raiding"]
    },
    "rituals": {
      "religious": ["Blót (sacrificial rituals)", "Sumbel (ritual drinking)"],
      "life_cycle": {
        "birth": "Naming ceremonies where the father would acknowledge the child",
        "death": "Burial with grave goods or cremation, sometimes in ships"
      }
    },
    "entertainment": {
      "games": ["Hnefatafl (board game)", "Dice games", "Physical contests"],
      "music": ["Frame drums", "Bone flutes", "Lyres"]
    },
    "taboos_and_codes": {
      "honor_concepts": ["Maintaining personal and family honor", "Fulfilling oaths"],
      "taboos": ["Oath-breaking", "Cowardice", "Refusing hospitality"]
    }
  },
  "language_cues": {
    "common_phrases": {
      "greetings": [
        {
          "original": "Heill",
          "meaning": "Hail/Hello"
        }
      ],
      "farewells": [
        {
          "original": "Vertu heill",
          "meaning": "Farewell/Be well"
        }
      ],
      "oaths": [
        {
          "original": "Ek sver við goðin",
          "meaning": "I swear by the gods"
        }
      ]
    },
    "naming_conventions": {
      "personal_names": {
        "patterns": ["Given name + patronymic (e.g., Erik Haraldsson)"],
        "common_elements": ["Thor-", "As-", "-ulf", "-mund"]
      },
      "place_names": {
        "patterns": ["Descriptive elements + geographic features"]
      }
    },
    "language_structure": {
      "formal_speech": "Formal speech patterns often included kennings and elaborate metaphors",
      "poetry": "Skaldic poetry used complex verse forms with internal rhyme and alliteration"
    },
    "writing_system": {
      "scripts": ["Elder Futhark", "Younger Futhark"],
      "materials": ["Stone (rune stones)", "Wood", "Bone", "Metal"]
    }
  },
  "environmental_elements": {
    "geography": {
      "terrain": ["Fjords", "Mountains", "Forests", "Islands", "Coastal areas"],
      "settlements": "Villages were typically located near water sources and arable land"
    },
    "climate": {
      "seasons": {
        "winter": "Long, harsh winters with limited daylight and heavy snow",
        "summer": "Short, mild summers with long days"
      },
      "weather": ["Strong winds", "Heavy snowfall", "Rain", "Coastal fog"]
    },
    "flora_and_fauna": {
      "plants": ["Pine", "Spruce", "Birch", "Oak", "Barley", "Rye"],
      "animals": ["Cattle", "Sheep", "Goats", "Horses", "Bears", "Wolves", "Reindeer"]
    },
    "lighting_conditions": {
      "natural": "Extreme seasonal variation with midnight sun in summer and polar night in winter",
      "artificial": ["Hearth fires", "Oil lamps", "Tallow candles"]
    },
    "soundscape": {
      "natural": ["Wind through trees", "Ocean waves", "Bird calls"],
      "human": ["Hammering of smiths", "Animal calls", "Ship-building sounds"]
    }
  }
}
"""
        
        prompt = f"""
        {emphasis}Your task is to generate a {detail_level} Period and Cultural Pack (PAC) for {culture} during {time_period}.
        
        The PAC should include accurate historical information organized according to the following structure:
        
        {sections_text}
        
        For each section, provide accurate, historically-grounded information that would help creators 
        develop stories, visuals, or other content set in this time and place with strong historical integrity.
        
        {emphasis}Your response must be a VALID JSON object with the following structure (similar to this example, but with content specific to {culture} during {time_period}).{style_note}
        
        {example_json}
        
        PAC Metadata:
        - title: "{culture}"
        - period: "{time_period}"
        - regions: Accurate geographic regions for this culture/period
        - tags: Relevant tags for categorizing this PAC
        - description: A brief description of the culture and period
        
        {emphasis}DO NOT include any explanations, markdown formatting, or ```json code blocks. ONLY provide the JSON object itself.
        """
        
        return prompt