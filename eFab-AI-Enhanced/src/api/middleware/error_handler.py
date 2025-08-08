"""
Error handling middleware
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
import traceback

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """Global error handler for all requests"""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # Log the error with full traceback
        logger.error(f"Unhandled error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": str(e),
                "path": str(request.url.path)
            }
        )