# Whereforth

Whereforth is an AI co-pilot for creators who want to build immersive stories grounded in real history and culture. At the heart of it are PACs (Period and Cultural Packs) — plug-and-play historical modules designed to guide the generation of environments, visuals, behaviors, and language that align with real-world periods and cultures.

## Overview

This proof of concept (POC) demonstrates how Gemini's structured output capabilities can be leveraged to generate rich, historically accurate content in the form of Period and Cultural Packs (PACs).

## Key Features

- **PAC Generation**: Generate structured Period and Cultural Packs for any historical period and culture
- **Structured Output**: PACs are organized into sections covering visual elements, cultural behaviors, language cues, and environmental elements
- **API Access**: Access the PAC generation functionality via a FastAPI endpoint
- **User Interface**: Explore and generate PACs using a Streamlit interface

## PAC Structure

Each PAC contains:

- **Visual Elements**: Architecture, clothing, artifacts, art styles, and color palettes
- **Cultural Behaviors**: Social structure, daily life, rituals, entertainment, taboos, and codes
- **Language Cues**: Common phrases, naming conventions, language structure, and writing systems
- **Environmental Elements**: Geography, climate, flora/fauna, lighting conditions, and soundscape

## Getting Started

### Prerequisites

- Python 3.8+
- Google API key with access to Gemini API

### Installation

1. Clone the repository:
```bash
git https://github.com/Reynold97/whereforth.git
cd whereforth
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.api.main:app --reload
```

2. Start the Streamlit UI:
```bash
streamlit run app/ui/streamlit_app.py
```

## Usage

### Web UI

1. Open your browser and navigate to the Streamlit UI (default: http://localhost:8501)
2. Select or enter a culture and time period
3. Click "Generate PAC"
4. Explore the generated PAC using the tabs
5. Download the PAC as a JSON file

### API

The API provides an endpoint for generating PACs:

```
POST /api/generate_pac
```

Request body:
```json
{
  "culture": "Viking Age Scandinavia",
  "time_period": "793-1066 CE",
  "detailed": false
}
```

## Future Enhancements

- Use LLM structured outputs for more fidelity
- Use search tools for grounded answers
- Use Wikipedia integration tools for information retrieval
- Integration with image generation tools
- PAC validation and quality assessment
- Fine-tuning for specific historical periods
- User feedback and correction mechanisms
- Expansion of the PAC schema to include more detailed information
- Integrations with storytelling and worldbuilding tools

## License

[MIT License](LICENSE)