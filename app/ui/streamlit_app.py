import streamlit as st
import json
import os
import sys
import time
from datetime import datetime

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="Whereforth - PAC Generator",
    page_icon="🧪",
    layout="wide",
)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.schemas.simple_pac_schemas import SimplePAC
from app.services.gemini_service import GeminiService
from app.core.pac_generator import PACGenerator
from app.utils.helpers import save_pac_to_file, list_available_pacs, load_pac_from_file
from app.config import settings

# Initialize the Gemini service
@st.cache_resource
def get_generator():
    return PACGenerator()

pac_generator = get_generator()

# Sidebar
st.sidebar.title("Whereforth")
st.sidebar.subheader("PAC Generator")

# Input form
with st.sidebar.form("pac_form"):
    st.write("### Generate New PAC")
    
    # Example time periods and cultures
    example_cultures = [
        "Viking Age Scandinavia",
        "Edo Japan", 
        "Ancient Mesopotamia",
        "Weimar Republic Germany",
        "Renaissance Italy",
        "Incan Peru",
        "Tang Dynasty China",
        "Mughal India",
        "Ottoman Empire",
        "Victorian England"
    ]
    
    # Let user select or enter custom
    culture_option = st.selectbox(
        "Select a Culture/Period or enter custom below:",
        ["Custom"] + example_cultures
    )
    
    if culture_option == "Custom":
        culture = st.text_input("Culture/Period", "")
    else:
        culture = culture_option
    
    time_period = st.text_input("Time Period (e.g., '793-1066 CE')", "")
    detailed = st.checkbox("Generate Detailed PAC", value=False)
    
    submit_button = st.form_submit_button(label="Generate PAC")

# Main content
st.title("Whereforth - Period and Cultural Pack (PAC) Generator")
st.markdown("""
This tool generates Period and Cultural Packs (PACs) that capture the essence of specific 
historical periods and cultures. These PACs can then be used to guide AI-generated content 
to ensure historical accuracy.

A PAC contains structured information about:
- **Visual Elements**: architecture, clothing, artifacts, art styles, color palettes
- **Cultural Behaviors**: social structure, daily life, rituals, entertainment, taboos
- **Language Cues**: common phrases, naming conventions, language structure
- **Environmental Elements**: geography, climate, flora/fauna, lighting conditions, sounds
""")

# Handle form submission
if submit_button and culture and time_period:
    with st.spinner(f"Generating PAC for {culture} during {time_period}..."):
        try:
            # Start timer
            start_time = time.time()
            
            # Call the Gemini service to generate a PAC
            pac = pac_generator.generate_pac(
                culture=culture,
                time_period=time_period,
                detailed=detailed
            )
            
            # End timer
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Display success
            st.success(f"PAC generated successfully in {generation_time:.2f} seconds!")
            
            # Save PAC to file
            title_slug = culture.replace(" ", "_").lower()
            filename = f"{title_slug}.json"
            filepath = save_pac_to_file(pac, filename)
            
            # Download button
            st.download_button(
                label="Download PAC",
                data=pac.model_dump_json(indent=2),
                file_name=filename,
                mime="application/json",
                key="download_generated_pac",
            )
            
            # Display PAC sections
            st.header("PAC Metadata")
            st.json(pac.pac_metadata.model_dump())
            
            # Create tabs for each section
            tabs = st.tabs([
                "Visual Elements", 
                "Cultural Behaviors", 
                "Language Cues", 
                "Environmental Elements"
            ])
            
            # Visual Elements tab
            with tabs[0]:
                st.subheader("Visual Elements")
                
                st.write("### Architecture")
                st.json(pac.visual_elements.architecture)
                
                st.write("### Clothing")
                st.json(pac.visual_elements.clothing)
                
                st.write("### Artifacts")
                st.json(pac.visual_elements.artifacts)
                
                st.write("### Art Motifs")
                st.json(pac.visual_elements.art_motifs)
                
                st.write("### Color Palette")
                st.json(pac.visual_elements.color_palette)
            
            # Cultural Behaviors tab
            with tabs[1]:
                st.subheader("Cultural Behaviors")
                
                st.write("### Social Structure")
                st.json(pac.cultural_behaviors.social_structure)
                
                st.write("### Daily Life")
                st.json(pac.cultural_behaviors.daily_life)
                
                st.write("### Rituals")
                st.json(pac.cultural_behaviors.rituals)
                
                st.write("### Entertainment")
                st.json(pac.cultural_behaviors.entertainment)
                
                st.write("### Taboos and Codes")
                st.json(pac.cultural_behaviors.taboos_and_codes)
            
            # Language Cues tab
            with tabs[2]:
                st.subheader("Language Cues")
                
                st.write("### Common Phrases")
                st.json(pac.language_cues.common_phrases)
                
                st.write("### Naming Conventions")
                st.json(pac.language_cues.naming_conventions)
                
                st.write("### Language Structure")
                st.json(pac.language_cues.language_structure)
                
                if pac.language_cues.writing_system:
                    st.write("### Writing System")
                    st.json(pac.language_cues.writing_system)
            
            # Environmental Elements tab
            with tabs[3]:
                st.subheader("Environmental Elements")
                
                st.write("### Geography")
                st.json(pac.environmental_elements.geography)
                
                st.write("### Climate")
                st.json(pac.environmental_elements.climate)
                
                st.write("### Flora and Fauna")
                st.json(pac.environmental_elements.flora_and_fauna)
                
                st.write("### Lighting Conditions")
                st.json(pac.environmental_elements.lighting_conditions)
                
                st.write("### Soundscape")
                st.json(pac.environmental_elements.soundscape)
                
        except Exception as e:
            st.error(f"Error generating PAC: {str(e)}")
            st.exception(e)
elif submit_button:
    st.warning("Please provide both Culture and Time Period to generate a PAC.")

# Display previously generated PACs
st.header("Previously Generated PACs")
pac_files = list_available_pacs()
if pac_files:
    selected_pac = st.selectbox("Select a PAC", pac_files)
    if selected_pac:
        try:
            filepath = os.path.join(settings.PAC_DIR, selected_pac)
            pac = load_pac_from_file(filepath)
            
            # Display basic info
            st.subheader(pac.pac_metadata.title)
            st.write(f"**Period:** {pac.pac_metadata.period}")
            st.write(f"**Regions:** {', '.join(pac.pac_metadata.regions)}")
            st.write(f"**Description:** {pac.pac_metadata.description}")
            
            # Download button
            with open(filepath, "r", encoding="utf-8") as f:
                pac_json = f.read()
            
            st.download_button(
                label="Download PAC",
                data=pac_json,
                file_name=selected_pac,
                mime="application/json",
                key="download_existing_pac",
            )
            
            # Create tabs for each section
            tabs = st.tabs([
                "Visual Elements", 
                "Cultural Behaviors", 
                "Language Cues", 
                "Environmental Elements"
            ])
            
            # Visual Elements tab
            with tabs[0]:
                st.subheader("Visual Elements")
                
                st.write("### Architecture")
                st.json(pac.visual_elements.architecture)
                
                st.write("### Clothing")
                st.json(pac.visual_elements.clothing)
                
                st.write("### Artifacts")
                st.json(pac.visual_elements.artifacts)
                
                st.write("### Art Motifs")
                st.json(pac.visual_elements.art_motifs)
                
                st.write("### Color Palette")
                st.json(pac.visual_elements.color_palette)
            
            # Cultural Behaviors tab
            with tabs[1]:
                st.subheader("Cultural Behaviors")
                
                st.write("### Social Structure")
                st.json(pac.cultural_behaviors.social_structure)
                
                st.write("### Daily Life")
                st.json(pac.cultural_behaviors.daily_life)
                
                st.write("### Rituals")
                st.json(pac.cultural_behaviors.rituals)
                
                st.write("### Entertainment")
                st.json(pac.cultural_behaviors.entertainment)
                
                st.write("### Taboos and Codes")
                st.json(pac.cultural_behaviors.taboos_and_codes)
            
            # Language Cues tab
            with tabs[2]:
                st.subheader("Language Cues")
                
                st.write("### Common Phrases")
                st.json(pac.language_cues.common_phrases)
                
                st.write("### Naming Conventions")
                st.json(pac.language_cues.naming_conventions)
                
                st.write("### Language Structure")
                st.json(pac.language_cues.language_structure)
                
                if pac.language_cues.writing_system:
                    st.write("### Writing System")
                    st.json(pac.language_cues.writing_system)
            
            # Environmental Elements tab
            with tabs[3]:
                st.subheader("Environmental Elements")
                
                st.write("### Geography")
                st.json(pac.environmental_elements.geography)
                
                st.write("### Climate")
                st.json(pac.environmental_elements.climate)
                
                st.write("### Flora and Fauna")
                st.json(pac.environmental_elements.flora_and_fauna)
                
                st.write("### Lighting Conditions")
                st.json(pac.environmental_elements.lighting_conditions)
                
                st.write("### Soundscape")
                st.json(pac.environmental_elements.soundscape)
                
        except Exception as e:
            st.error(f"Error loading PAC: {str(e)}")
            st.exception(e)
else:
    st.info("No PACs generated yet. Use the form to generate your first PAC!")