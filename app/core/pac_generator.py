from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

from app.schemas.simple_pac_schemas import SimplePAC, PACMetadata, VisualElements, CulturalBehaviors, LanguageCues, EnvironmentalElements, PAC_TEMPLATE
from app.services.gemini_service import GeminiService

class PACGenerator:
    """
    Generator for Period and Cultural Packs (PACs).
    Contains all logic for constructing prompts and generating PACs section by section.
    """
    
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        """
        Initialize the PAC Generator with a Gemini service
        
        Args:
            gemini_service (GeminiService, optional): The Gemini service to use.
                If None, a new one will be created.
        """
        self.gemini_service = gemini_service or GeminiService()
    
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
        
        # Generate each section separately
        sections = [
            "pac_metadata",
            "visual_elements",
            "cultural_behaviors",
            "language_cues",
            "environmental_elements"
        ]
        
        pac_data = {}
        
        # Generate sections one by one
        for section in sections:
            try:
                # Generate the section
                section_data = self._generate_section(culture, time_period, section, detailed, max_retries)
                
                # Add the section to the PAC data
                pac_data[section] = section_data
                
                # For metadata section, ensure our required fields are preserved
                if section == "pac_metadata":
                    pac_data[section]["created_at"] = metadata.created_at
                    pac_data[section]["source"] = metadata.source
                    pac_data[section]["version"] = metadata.version
                
            except Exception as e:
                # If a section fails, log it but continue
                print(f"Error generating section '{section}': {str(e)}")
                
                # Use empty values as fallback for this section
                if section == "pac_metadata":
                    pac_data[section] = metadata.model_dump()
                else:
                    section_model_classes = {
                        "visual_elements": VisualElements,
                        "cultural_behaviors": CulturalBehaviors,
                        "language_cues": LanguageCues,
                        "environmental_elements": EnvironmentalElements
                    }
                    pac_data[section] = section_model_classes[section]().model_dump()
        
        # Create PAC object
        try:
            pac = SimplePAC.model_validate(pac_data)
            return pac
        except Exception as e:
            # If validation fails, raise an error
            raise ValueError(f"Failed to create valid PAC from sections: {str(e)}")
    
    def _generate_section(self, culture: str, time_period: str, section_name: str, detailed: bool = False, max_retries: int = 3) -> Dict[str, Any]:
        """
        Generate a single section of the PAC
        
        Args:
            culture (str): The culture to generate a PAC for
            time_period (str): The time period
            section_name (str): The name of the section to generate
            detailed (bool): Whether to generate a detailed section
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            Dict[str, Any]: The generated section data
        """
        errors = []
        
        for attempt in range(max_retries):
            try:
                # Create a prompt specific to this section
                prompt = self._create_section_prompt(culture, time_period, section_name, detailed, attempt)
                
                # Generate the section using the Gemini service
                response_text = self.gemini_service.generate_content(prompt)
                
                # Extract JSON from the response
                section_data = self.gemini_service.extract_json_from_text(response_text)
                
                # If we're extracting a specific section from a full PAC response
                if section_name in section_data:
                    # The response included the section name as a key
                    return section_data[section_name]
                else:
                    # Assume the response is just the section content
                    return section_data
                
            except Exception as e:
                errors.append(f"Attempt {attempt+1} failed: {str(e)}")
                
                # If this isn't the last attempt, continue to the next one
                if attempt < max_retries - 1:
                    continue
                
                # If all attempts fail, raise an error with details about each attempt
                error_details = "\n".join(errors)
                raise ValueError(f"All {max_retries} attempts failed to generate section '{section_name}':\n{error_details}")
    
    def _create_section_prompt(self, culture: str, time_period: str, section_name: str, detailed: bool = False, attempt: int = 0) -> str:
        """
        Create a prompt for generating a specific section of a PAC
        
        Args:
            culture (str): The culture to generate a PAC for
            time_period (str): The time period
            section_name (str): The name of the section to generate
            detailed (bool): Whether to generate a detailed section
            attempt (int): The current attempt number
            
        Returns:
            str: The prompt
        """
        detail_level = "detailed and comprehensive" if detailed else "concise but informative"
        emphasis = ["", "IMPORTANT: ", "CRITICAL: "][min(attempt, 2)]
        
        # Find the section in the PAC_TEMPLATE
        section_info = None
        for section in PAC_TEMPLATE["sections"]:
            if section["name"] == section_name:
                section_info = section
                break
        
        # If it's the metadata section, handle it specially
        if section_name == "pac_metadata":
            return self._create_metadata_prompt(culture, time_period, attempt)
        
        # If no section info found (shouldn't happen), use a generic prompt
        if section_info is None:
            return f"""
            Generate the {section_name} section for a historical and cultural pack about {culture} during {time_period}.
            Provide detailed and accurate information formatted as a JSON object.
            """
        
        # Build the section description
        section_text = f"## {section_info['name'].title()}: {section_info['description']}\n\n"
        
        for subsection in section_info["subsections"]:
            section_text += f"### {subsection['name'].title()}: {subsection['description']}\n"
            
            for detail in subsection["required_details"]:
                section_text += f"- {detail}\n"
            
            section_text += "\n"
        
        # Get example section from our full example
        example_section = self._get_example_section(section_name)
        
        prompt = f"""
        {emphasis}Generate the {section_name} section for a Period and Cultural Pack (PAC) about {culture} during {time_period}.
        
        Your response should be {detail_level} and historically accurate, covering:
        
        {section_text}
        
        Format your response as a valid JSON object structured like this example (but with content specific to {culture} during {time_period}):
        
        {example_section}
        
        {emphasis}Make sure to include ALL subsections shown in the example. Do not leave any subsections empty.
        
        Return ONLY the JSON for the {section_name} section - no explanations, markdown, or code blocks.
        """
        
        return prompt
    
    def _create_metadata_prompt(self, culture: str, time_period: str, attempt: int = 0) -> str:
        """
        Create a prompt specifically for the metadata section
        
        Args:
            culture (str): The culture
            time_period (str): The time period
            attempt (int): The attempt number
            
        Returns:
            str: The prompt
        """
        emphasis = ["", "IMPORTANT: ", "CRITICAL: "][min(attempt, 2)]
        
        prompt = f"""
        {emphasis}Create metadata for a Period and Cultural Pack (PAC) about {culture} during {time_period}.
        
        Include the following information:
        - title: A concise, descriptive title (e.g., "{culture}")
        - period: The time period ("{time_period}")
        - regions: A list of geographic regions relevant to this culture and period
        - tags: A list of relevant tags for categorizing this PAC
        - description: A brief overview of the culture and period (1-3 sentences)
        
        Format your response as a valid JSON object like this:
        
        {{
          "title": "Viking Age Scandinavia",
          "period": "793-1066 CE",
          "regions": ["Norway", "Denmark", "Sweden", "Iceland"],
          "tags": ["Vikings", "Norse", "Medieval", "Scandinavia"],
          "description": "The Viking Age was a period during the Middle Ages when Norsemen known as Vikings undertook large-scale raiding, colonizing, conquest, and trading throughout Europe and reached North America."
        }}
        
        Return ONLY the JSON - no explanations, markdown, or code blocks.
        """
        
        return prompt
    
    def _get_example_section(self, section_name: str) -> str:
        """
        Get an example of a specific section from our example PAC
        
        Args:
            section_name (str): The name of the section
            
        Returns:
            str: The example section as a JSON string
        """
        # This is a simplified example PAC with all the sections we need
        examples = {
            "pac_metadata": """
{
  "title": "Viking Age Scandinavia",
  "period": "793-1066 CE",
  "regions": ["Norway", "Denmark", "Sweden", "Iceland"],
  "tags": ["Vikings", "Norse", "Medieval", "Scandinavia"],
  "description": "The Viking Age was a period during the Middle Ages when Norsemen known as Vikings undertook large-scale raiding, colonizing, conquest, and trading throughout Europe and reached North America."
}
""",
            "visual_elements": """
{
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
}
""",
            "cultural_behaviors": """
{
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
}
""",
            "language_cues": """
{
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
}
""",
            "environmental_elements": """
{
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
"""
        }
        
        return examples.get(section_name, "{}")