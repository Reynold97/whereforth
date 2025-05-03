from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.pac_schemas import PAC

class PACRequest(BaseModel):
    culture: str = Field(..., description="Culture to generate a PAC for (e.g., 'Viking Age Scandinavia')")
    time_period: str = Field(..., description="Time period (e.g., '793-1066 CE')")
    detailed: bool = Field(False, description="Whether to generate a detailed PAC")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "culture": "Viking Age Scandinavia",
                "time_period": "793-1066 CE",
                "detailed": False
            }
        }
    }

class PACResponse(BaseModel):
    pac: PAC = Field(..., description="The generated PAC")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Status message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "pac": {
                    "pac_metadata": {
                        "title": "Viking Age Scandinavia",
                        "period": "793-1066 CE",
                        "regions": ["Norway", "Denmark", "Sweden", "Iceland"],
                        "tags": ["Vikings", "Norse", "Medieval", "Scandinavia"],
                        "version": "0.1.0",
                        "description": "A historical framework capturing the culture of Viking Age Scandinavia",
                        "created_at": "2023-04-30T12:00:00",
                        "source": "Gemini"
                    }
                },
                "status": "success",
                "message": "PAC generated successfully"
            }
        }
    }

class ErrorResponse(BaseModel):
    status: str = Field("error", description="Status of the request")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "error",
                "message": "Failed to generate PAC",
                "detail": "Invalid time period format"
            }
        }
    }