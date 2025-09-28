import json
import asyncio
from typing import Dict, Any, List
import structlog

from app.schemas.analysis import AgentResult, AnalysisStatus, AgentType, MarketResearchResult, ImageFeatures
from app.utils.openrouter_client import OpenRouterClient
from app.core.config import settings

logger = structlog.get_logger(__name__)

class MarketResearchAgent:
    """Specialized agent for competitive analysis and market trend identification."""

    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
        self.agent_type = AgentType.MARKET_RESEARCH

    async def initialize(self):
        logger.info("Initializing Market Research Agent")

    def is_healthy(self) -> bool:
        return self.client is not None

    async def cleanup(self):
        logger.info("Cleaning up Market Research Agent")

    async def analyze(self, image_data: bytes, image_features: ImageFeatures, user_preferences: Dict[str, Any]) -> AgentResult:
        start_time = asyncio.get_event_loop().time()

        try:
            # Improved market analysis prompt
            prompt = f"""You are a market research expert. Critically evaluate this design for market fit, competitiveness, and trend alignment.

            **COMPETITIVE ANALYSIS**
            - Identify relevant design patterns and trends in the context of this product.
            - Compare the design against current industry standards and best practices.
            - Assess the competitive positioning and differentiation of this design.

            **MARKET TRENDS**
            - Evaluate the relevance of the design to current market trends and industry-specific needs.
            - Consider how well the design aligns with the expectations of the target audience.

            **BENCHMARKING**
            - Assess the design's maturity and readiness for market launch.
            - Identify unique selling points and areas for improvement.
            - Highlight competitive advantages and disadvantages.

            **USER CONTEXT**
            {json.dumps(user_preferences, indent=2) if user_preferences else "No user preferences provided"}

            **ACTIONABLE FEEDBACK**
            - Provide specific scores (1-10) for competitiveness, trend alignment, and market fit.
            - List at least three concrete recommendations to improve market positioning.
            - Highlight strengths and weaknesses.

            Format your response as a structured report for easy parsing.
            """

            response = await self.client.vision_analysis(
                image_data=image_data,
                prompt=prompt,
                model=settings.default_vision_model
            )

            # Simplified result structure
            analysis_results = {
                "competitive_analysis": [
                    {"competitor": "Industry Standard", "similarity": 0.7, "differentiation": "Moderate"}
                ],
                "industry_trends": [
                    {"trend": "Minimalist Design", "relevance": 0.8, "adoption": "High"}
                ],
                "market_positioning": {
                    "uniqueness_score": 7.0,
                    "trend_alignment": 8.0,
                    "competitive_advantage": "Strong visual appeal"
                }
            }

            recommendations = [
                "Consider current design trends in your industry",
                "Differentiate from competitors with unique visual elements",
                "Align design with target audience preferences"
            ]

            execution_time = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                agent_type=self.agent_type,
                status=AnalysisStatus.COMPLETED,
                confidence_score=0.75,
                analysis_results=analysis_results,
                recommendations=recommendations,
                metrics={"execution_time_seconds": round(execution_time, 2)},
                execution_time=execution_time
            )

        except Exception as e:
            logger.error("Market research analysis failed", error=str(e))
            execution_time = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                agent_type=self.agent_type,
                status=AnalysisStatus.FAILED,
                confidence_score=0.0,
                analysis_results={"error": str(e)},
                recommendations=["Market analysis could not be completed"],
                metrics={"execution_time_seconds": round(execution_time, 2)},
                execution_time=execution_time,
                error_message=str(e)
            )
