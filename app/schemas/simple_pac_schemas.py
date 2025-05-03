from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class PACMetadata(BaseModel):
    """Metadata for a Period and Cultural Pack (PAC)"""
    title: str = Field(..., description="Title of the PAC (e.g., 'Viking Age Scandinavia')")
    period: str = Field(..., description="Time period covered (e.g., '793-1066 CE')")
    regions: List[str] = Field(..., description="Geographic regions covered")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    description: str = Field(..., description="Brief description of the culture and period")
    version: str = Field(default="0.1.0", description="Version of the PAC")
    created_at: Optional[str] = None
    source: Optional[str] = None

class VisualElements(BaseModel):
    """Visual elements of the culture"""
    architecture: Dict[str, Any] = Field(
        default_factory=dict,
        description="Architecture types and their features"
    )
    clothing: Dict[str, Any] = Field(
        default_factory=dict,
        description="Clothing by gender and occasion"
    )
    artifacts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Important artifacts and tools"
    )
    art_motifs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Artistic styles and common motifs"
    )
    color_palette: Dict[str, Any] = Field(
        default_factory=dict,
        description="Common colors used in the period"
    )

class CulturalBehaviors(BaseModel):
    """Cultural behaviors, social structures, rituals, and codes of conduct"""
    social_structure: Dict[str, Any] = Field(
        default_factory=dict,
        description="Social hierarchy and roles"
    )
    daily_life: Dict[str, Any] = Field(
        default_factory=dict,
        description="Daily activities, food, family life"
    )
    rituals: Dict[str, Any] = Field(
        default_factory=dict,
        description="Religious and cultural practices"
    )
    entertainment: Dict[str, Any] = Field(
        default_factory=dict,
        description="Games, music, storytelling"
    )
    taboos_and_codes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Honor codes, taboos, social norms"
    )

class LanguageCues(BaseModel):
    """Language patterns, common phrases, naming conventions"""
    common_phrases: Dict[str, Any] = Field(
        default_factory=dict,
        description="Greetings, farewells, oaths, etc."
    )
    naming_conventions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Personal names, titles, etc."
    )
    language_structure: Dict[str, Any] = Field(
        default_factory=dict,
        description="Speech patterns, formal/informal, etc."
    )
    writing_system: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Writing systems, alphabets, etc."
    )

class EnvironmentalElements(BaseModel):
    """Geography, climate, flora/fauna, sensory environment"""
    geography: Dict[str, Any] = Field(
        default_factory=dict,
        description="Terrain, settlements, geographical features"
    )
    climate: Dict[str, Any] = Field(
        default_factory=dict,
        description="Seasons, weather patterns"
    )
    flora_and_fauna: Dict[str, Any] = Field(
        default_factory=dict,
        description="Plants and animals"
    )
    lighting_conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Natural and artificial light"
    )
    soundscape: Dict[str, Any] = Field(
        default_factory=dict,
        description="Common sounds (natural, settlement, cultural)"
    )

class SimplePAC(BaseModel):
    """Simplified Period and Cultural Pack (PAC) schema"""
    pac_metadata: PACMetadata
    visual_elements: VisualElements = Field(default_factory=VisualElements)
    cultural_behaviors: CulturalBehaviors = Field(default_factory=CulturalBehaviors)
    language_cues: LanguageCues = Field(default_factory=LanguageCues)
    environmental_elements: EnvironmentalElements = Field(default_factory=EnvironmentalElements)

# Template for generating PAC prompts
PAC_TEMPLATE = {
    "sections": [
        {
            "name": "visual_elements",
            "description": "Visual aspects of the culture including architecture, clothing, artifacts, and art",
            "subsections": [
                {
                    "name": "architecture",
                    "description": "Common building types, construction methods, and materials",
                    "required_details": [
                        "Dwellings (homes, common structures)",
                        "Public structures (gathering places, markets)",
                        "Religious structures (temples, shrines)",
                        "Construction techniques and materials"
                    ]
                },
                {
                    "name": "clothing",
                    "description": "Garments, fabrics, and accessories worn by different genders and social classes",
                    "required_details": [
                        "Everyday clothing for different genders",
                        "Ceremonial or special occasion clothing",
                        "Materials, colors, and decorative elements",
                        "Status indicators in clothing"
                    ]
                },
                {
                    "name": "artifacts",
                    "description": "Common tools, weapons, household items, and culturally significant objects",
                    "required_details": [
                        "Weapons and armor",
                        "Tools for work and daily life",
                        "Household items",
                        "Transportation methods"
                    ]
                },
                {
                    "name": "art_motifs",
                    "description": "Artistic styles, decoration patterns, and symbolic imagery",
                    "required_details": [
                        "Major art styles and when they were used",
                        "Common motifs and symbols",
                        "Materials and methods for artistic expression",
                        "Culturally significant imagery"
                    ]
                },
                {
                    "name": "color_palette",
                    "description": "Colors commonly used in clothing, art, and decoration",
                    "required_details": [
                        "Natural colors available",
                        "Dyes and pigments used",
                        "Status-related color associations"
                    ]
                }
            ]
        },
        {
            "name": "cultural_behaviors",
            "description": "Social structure, daily life, rituals, and cultural practices",
            "subsections": [
                {
                    "name": "social_structure",
                    "description": "Hierarchy, roles, and social organization",
                    "required_details": [
                        "Social classes and their roles",
                        "Gender roles and responsibilities",
                        "Family structure and kinship",
                        "Leadership and power structures"
                    ]
                },
                {
                    "name": "daily_life",
                    "description": "Common activities, food, work, and family life",
                    "required_details": [
                        "Typical daily routines",
                        "Food and diet",
                        "Occupations and labor",
                        "Family life and childrearing"
                    ]
                },
                {
                    "name": "rituals",
                    "description": "Religious practices, ceremonies, and life cycle events",
                    "required_details": [
                        "Religious or spiritual practices",
                        "Birth, coming of age, marriage, and death customs",
                        "Seasonal celebrations and festivals",
                        "Important ceremonies"
                    ]
                },
                {
                    "name": "entertainment",
                    "description": "Games, music, storytelling, and leisure activities",
                    "required_details": [
                        "Games and sports",
                        "Music and instruments",
                        "Storytelling traditions",
                        "Other leisure activities"
                    ]
                },
                {
                    "name": "taboos_and_codes",
                    "description": "Social norms, honor codes, taboos, and expected behaviors",
                    "required_details": [
                        "Behavioral expectations",
                        "Taboos and forbidden activities",
                        "Honor and shame concepts",
                        "Hospitality customs"
                    ]
                }
            ]
        },
        {
            "name": "language_cues",
            "description": "Language patterns, phrases, naming conventions, and communication styles",
            "subsections": [
                {
                    "name": "common_phrases",
                    "description": "Frequently used expressions and their meanings",
                    "required_details": [
                        "Greeting and farewell phrases",
                        "Common expressions and sayings",
                        "Formal speech elements",
                        "Oaths or exclamations"
                    ]
                },
                {
                    "name": "naming_conventions",
                    "description": "How people and places are named",
                    "required_details": [
                        "Personal naming patterns",
                        "Place naming conventions",
                        "Title systems",
                        "Meaning of common names"
                    ]
                },
                {
                    "name": "language_structure",
                    "description": "Speech patterns and communication styles",
                    "required_details": [
                        "Formal vs informal speech",
                        "Status indicators in language",
                        "Poetic or specialized language forms",
                        "Common metaphors or expressions"
                    ]
                },
                {
                    "name": "writing_system",
                    "description": "Writing methods, if applicable",
                    "required_details": [
                        "Alphabets or writing systems",
                        "Common inscriptions or texts",
                        "Writing materials and methods",
                        "Literacy and who could write"
                    ]
                }
            ]
        },
        {
            "name": "environmental_elements",
            "description": "Geography, climate, flora/fauna, and sensory aspects of the environment",
            "subsections": [
                {
                    "name": "geography",
                    "description": "Physical landscape and settlement patterns",
                    "required_details": [
                        "Common terrain features",
                        "Settlement patterns",
                        "Important locations",
                        "Natural resources"
                    ]
                },
                {
                    "name": "climate",
                    "description": "Weather patterns, seasons, and climate conditions",
                    "required_details": [
                        "Seasonal variations",
                        "Typical weather conditions",
                        "Climate challenges and adaptations",
                        "Weather-related beliefs"
                    ]
                },
                {
                    "name": "flora_and_fauna",
                    "description": "Plants and animals in the environment",
                    "required_details": [
                        "Common plants (wild and cultivated)",
                        "Domestic animals",
                        "Wild animals",
                        "Culturally significant species"
                    ]
                },
                {
                    "name": "lighting_conditions",
                    "description": "Natural and artificial light",
                    "required_details": [
                        "Daylight patterns throughout the year",
                        "Artificial lighting methods",
                        "Light-related cultural practices",
                        "Visual atmosphere"
                    ]
                },
                {
                    "name": "soundscape",
                    "description": "Common sounds in the environment",
                    "required_details": [
                        "Natural sounds",
                        "Human activity sounds",
                        "Music and ceremonial sounds",
                        "Silence and noise patterns"
                    ]
                }
            ]
        }
    ]
}