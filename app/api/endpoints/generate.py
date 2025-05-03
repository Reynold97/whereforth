from fastapi import APIRouter, Depends, HTTPException
from app.schemas.api_schemas import PACRequest, PACResponse, ErrorResponse
from app.services.gemini_service import GeminiService
from app.utils.helpers import save_pac_to_file

router = APIRouter()

@router.post(
    "/generate_pac", 
    response_model=PACResponse,
    responses={
        200: {"model": PACResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_pac(
    request: PACRequest, 
    gemini_service: GeminiService = Depends(lambda: GeminiService())
):
    """
    Generate a Period and Cultural Pack (PAC) for the specified culture and time period
    """
    try:
        # Generate the PAC using the Gemini service
        pac = gemini_service.generate_pac(
            culture=request.culture,
            time_period=request.time_period,
            detailed=request.detailed
        )
        
        # Save the PAC to a file
        title_slug = request.culture.replace(" ", "_").lower()
        filename = f"{title_slug}.json"
        save_pac_to_file(pac, filename)
        
        # Return the PAC
        return PACResponse(
            pac=pac,
            status="success",
            message="PAC generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PAC: {str(e)}"
        )