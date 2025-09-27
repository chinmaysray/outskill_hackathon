from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
import asyncio
import json
import uuid
from typing import Dict, Any, List
import structlog

from app.core.config import settings
from app.services.orchestrator import AnalysisOrchestrator
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisState
from app.utils.image_processor import ImageProcessor
from app.utils.metrics import setup_metrics
from app.utils.rate_limiter import RateLimiter

# Setup structured logging
logger = structlog.get_logger(__name__)

# Global objects
analysis_orchestrator: AnalysisOrchestrator = None
image_processor: ImageProcessor = None
rate_limiter: RateLimiter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global analysis_orchestrator, image_processor, rate_limiter

    logger.info("Starting up Multimodal AI Design Analysis Suite...")

    try:
        # Initialize services
        image_processor = ImageProcessor()
        await image_processor.initialize()

        analysis_orchestrator = AnalysisOrchestrator()
        await analysis_orchestrator.initialize()

        rate_limiter = RateLimiter(
            max_calls=settings.rate_limit_calls,
            time_window=settings.rate_limit_period
        )

        # Setup metrics if enabled
        if settings.enable_metrics:
            setup_metrics(app)

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error("Failed to initialize application", error=str(e))
        raise

    yield

    # Cleanup
    logger.info("Shutting down application...")
    if analysis_orchestrator:
        await analysis_orchestrator.cleanup()
    if image_processor:
        await image_processor.cleanup()

    logger.info("Application shutdown completed")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A cutting-edge AI-powered design analysis platform with specialized agents",
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "status": "/api/v1/analysis/{analysis_id}/status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if core services are operational
        orchestrator_healthy = analysis_orchestrator and analysis_orchestrator.is_healthy()
        processor_healthy = image_processor and image_processor.is_healthy()

        status = "healthy" if orchestrator_healthy and processor_healthy else "degraded"

        return {
            "status": status,
            "timestamp": "2025-09-26T18:52:00Z",
            "services": {
                "orchestrator": "healthy" if orchestrator_healthy else "degraded",
                "image_processor": "healthy" if processor_healthy else "degraded"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post(f"{settings.api_prefix}/analyze")
async def analyze_design(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    user_preferences: str = "{}",
    brand_guidelines: str = "{}"
):
    """
    Main analysis endpoint that accepts an image and returns streaming analysis results.
    """
    try:
        # Rate limiting check
        client_id = "default"  # In production, use actual client identification
        if not await rate_limiter.allow_request(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Validate image
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Generate analysis ID
        analysis_id = str(uuid.uuid4())

        logger.info("Starting design analysis", analysis_id=analysis_id)

        # Process image
        image_bytes = await image.read()
        image_features = await image_processor.process_image(image_bytes)

        # Parse preferences
        try:
            user_prefs = json.loads(user_preferences) if user_preferences else {}
            brand_guide = json.loads(brand_guidelines) if brand_guidelines else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in preferences or guidelines")

        # Create analysis request
        analysis_request = AnalysisRequest(
            analysis_id=analysis_id,
            image_data=image_bytes,
            image_features=image_features,
            user_preferences=user_prefs,
            brand_guidelines=brand_guide,
            filename=image.filename
        )

        # Stream analysis results
        return StreamingResponse(
            analysis_orchestrator.stream_analysis(analysis_request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Analysis-ID": analysis_id
            }
        )

    except Exception as e:
        logger.error("Analysis failed", error=str(e), analysis_id=getattr(locals().get('analysis_request'), 'analysis_id', 'unknown'))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get(f"{settings.api_prefix}/analysis/{{analysis_id}}/status")
async def get_analysis_status(analysis_id: str):
    """Get the current status of an ongoing analysis."""
    try:
        status = await analysis_orchestrator.get_analysis_status(analysis_id)
        if not status:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return status

    except Exception as e:
        logger.error("Failed to get analysis status", analysis_id=analysis_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis status")

@app.get(f"{settings.api_prefix}/analysis/{{analysis_id}}/report")
async def get_analysis_report(analysis_id: str):
    """Get the complete analysis report for a completed analysis."""
    try:
        report = await analysis_orchestrator.get_analysis_report(analysis_id)
        if not report:
            raise HTTPException(status_code=404, detail="Analysis report not found")

        return report

    except Exception as e:
        logger.error("Failed to get analysis report", analysis_id=analysis_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis report")

@app.get(f"{settings.api_prefix}/models")
async def get_available_models():
    """Get list of available AI models and their capabilities."""
    return {
        "vision_models": [
            {
                "id": "openai/gpt-4-vision-preview",
                "name": "GPT-4 Vision",
                "capabilities": ["image_analysis", "visual_design", "ui_evaluation"]
            }
        ],
        "text_models": [
            {
                "id": "anthropic/claude-3-5-sonnet-20241022", 
                "name": "Claude 3.5 Sonnet",
                "capabilities": ["reasoning", "analysis", "critique"]
            }
        ],
        "code_models": [
            {
                "id": "meta-llama/codellama-34b-instruct",
                "name": "Code Llama",
                "capabilities": ["technical_analysis", "implementation_planning"]
            }
        ]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.error("HTTP exception", status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "http_error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error("Unexpected error", error=str(exc), type=type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": "server_error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
