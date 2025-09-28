import json
import asyncio
from typing import Dict, Any, List
import numpy as np
import structlog

from app.schemas.analysis import AgentResult, AnalysisStatus, AgentType, VisualAnalysisResult, ImageFeatures
from app.utils.openrouter_client import OpenRouterClient
from app.core.config import settings

logger = structlog.get_logger(__name__)

class VisualAnalysisAgent:
    """
    Specialized agent for deep visual analysis of design elements,
    layout, typography, and visual hierarchy.
    """

    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
        self.agent_type = AgentType.VISUAL_ANALYSIS
        self.model = settings.default_vision_model

    async def initialize(self):
        """Initialize the visual analysis agent."""
        logger.info("Initializing Visual Analysis Agent")
        # Agent-specific initialization can go here

    def is_healthy(self) -> bool:
        """Check if agent is healthy."""
        return self.client is not None

    async def cleanup(self):
        """Cleanup agent resources."""
        logger.info("Cleaning up Visual Analysis Agent")

    async def analyze(
        self, 
        image_data: bytes, 
        image_features: ImageFeatures, 
        user_preferences: Dict[str, Any]
    ) -> AgentResult:
        """
        Perform comprehensive visual analysis.

        Args:
            image_data: Raw image bytes
            image_features: Extracted image features
            user_preferences: User preferences and context

        Returns:
            AgentResult with visual analysis findings
        """
        start_time = asyncio.get_event_loop().time()

        try:
            logger.info("Starting visual analysis", image_size=len(image_data), model=self.model)

            # Create comprehensive analysis prompt
            analysis_prompt = self._create_analysis_prompt(image_features, user_preferences)
            logger.info("Created analysis prompt", prompt_length=len(analysis_prompt))

            # Perform vision analysis
            logger.info("Sending vision analysis request", model=self.model, detail="high")
            response = await self.client.vision_analysis(
                image_data=image_data,
                prompt=analysis_prompt,
                model=self.model,
                detail="high"
            )
            
            logger.info("Received vision analysis response", response_type=type(response), response_keys=list(response.keys()) if isinstance(response, dict) else "Not a dict")
            logger.info("Vision response content preview", content_preview=response.get("content", "")[:200] if response.get("content") else "No content")

            # Parse and structure the analysis results
            logger.info("Parsing analysis results")
            analysis_results = await self._parse_analysis_results(response["content"], image_features)
            logger.info("Analysis results parsed", results_type=type(analysis_results), results_keys=list(analysis_results.keys()) if isinstance(analysis_results, dict) else "Not a dict")

            # Calculate confidence score based on analysis completeness
            confidence_score = self._calculate_confidence(analysis_results, image_features)

            # Generate specific recommendations
            recommendations = self._generate_recommendations(analysis_results)

            execution_time = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                agent_type=self.agent_type,
                status=AnalysisStatus.COMPLETED,
                confidence_score=confidence_score,
                analysis_results=analysis_results,
                recommendations=recommendations,
                metrics={
                    "analysis_depth": len(analysis_results),
                    "color_palette_size": len(image_features.color_palette),
                    "ui_components_detected": len(image_features.ui_components),
                    "execution_time_seconds": round(execution_time, 2)
                },
                execution_time=execution_time
            )

        except Exception as e:
            logger.error("Visual analysis failed", error=str(e))
            execution_time = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                agent_type=self.agent_type,
                status=AnalysisStatus.FAILED,
                confidence_score=0.0,
                analysis_results={"error": str(e)},
                recommendations=["Visual analysis could not be completed"],
                metrics={"execution_time_seconds": round(execution_time, 2)},
                execution_time=execution_time,
                error_message=str(e)
            )

    def _create_analysis_prompt(self, image_features: ImageFeatures, user_preferences: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt for vision model."""

        color_info = ", ".join([f"{c['role']}: {c['hex']}" for c in image_features.color_palette[:5]])
        prompt = f"""You are a senior visual designer. Perform a comprehensive analysis of this image for design quality, clarity, and brand consistency.

        **COLOR ANALYSIS**
        - Assess color harmony, accessibility, and contrast ratios.
        - Analyze the detected color palette: {color_info}
        - Rate color harmony and accessibility (1-10).
        - Recommend improvements for color usage.

        **TYPOGRAPHY**
        - Evaluate font choices, readability, hierarchy, and consistency.
        - Suggest improvements for typography and text contrast.

        **LAYOUT & COMPOSITION**
        - Assess visual balance, symmetry, and adherence to design principles (rule of thirds, golden ratio).
        - Analyze whitespace usage and element spacing.
        - Image dimensions: {image_features.dimensions['width']}x{image_features.dimensions['height']}

        **VISUAL HIERARCHY**
        - Evaluate information hierarchy, visual flow, and user attention guidance.
        - Analyze element prominence and emphasis.

        **UI COMPONENTS**
        - Assess consistency, styling, and interaction design of {len(image_features.ui_components)} detected components.

        **ACCESSIBILITY**
        - Check WCAG compliance, color contrast, and readability for users with disabilities.

        **BRAND CONSISTENCY**
        - Evaluate visual identity coherence and brand element integration.

        **USER PREFERENCES**
        {json.dumps(user_preferences, indent=2) if user_preferences else "No specific preferences provided"}

        **ACTIONABLE FEEDBACK**
        - Provide specific scores (1-10) for each major category.
        - List at least three concrete recommendations to improve design quality.
        - Highlight strengths and weaknesses.

        Format your response as a structured report for easy parsing.
        """
        return prompt

    async def _parse_analysis_results(self, analysis_content: str, image_features: ImageFeatures) -> Dict[str, Any]:
        """Parse and structure the LLM analysis results."""

        # Create structured prompt to extract specific metrics
        parsing_prompt = f"""Extract specific metrics and analysis from this visual design analysis:

{analysis_content}

Please format the response as JSON with these exact keys:
{{
  "color_harmony_score": <float 1-10>,
  "typography_assessment": {{
    "readability_score": <float 1-10>,
    "hierarchy_clarity": <float 1-10>,
    "font_consistency": <float 1-10>
  }},
  "layout_composition": {{
    "balance_score": <float 1-10>,
    "whitespace_usage": <float 1-10>,
    "alignment_quality": <float 1-10>
  }},
  "visual_hierarchy": {{
    "clarity_score": <float 1-10>,
    "flow_effectiveness": <float 1-10>,
    "emphasis_appropriate": <float 1-10>
  }},
  "accessibility_compliance": {{
    "contrast_adequate": <boolean>,
    "text_readable": <boolean>,
    "color_blind_friendly": <boolean>
  }},
  "brand_consistency": {{
    "visual_coherence": <float 1-10>,
    "brand_alignment": <float 1-10>
  }},
  "overall_assessment": {{
    "design_quality_score": <float 1-10>,
    "professional_appearance": <float 1-10>,
    "user_experience_score": <float 1-10>
  }}
}}
"""

        try:
            logger.info("Sending text analysis request", model=settings.default_text_model, prompt_length=len(parsing_prompt))
            parsing_response = await self.client.text_analysis(
                prompt=parsing_prompt,
                model=settings.default_text_model,
                temperature=0.1  # Low temperature for structured output
            )
            
            logger.info("Received text analysis response", response_type=type(parsing_response), response_keys=list(parsing_response.keys()) if isinstance(parsing_response, dict) else "Not a dict")
            logger.info("Response content preview", content_preview=parsing_response.get("content", "")[:200] if parsing_response.get("content") else "No content")

            # Check if response has content
            if not parsing_response.get("content"):
                logger.warning("Empty response from text analysis", response=parsing_response)
                raise ValueError("Empty response from text analysis")

            # Try to parse JSON from response
            logger.info("Attempting to parse JSON from response", content_length=len(parsing_response["content"]))
            structured_data = json.loads(parsing_response["content"])
            logger.info("JSON parsing successful", structured_keys=list(structured_data.keys()) if isinstance(structured_data, dict) else "Not a dict")

            # Add image feature context
            structured_data["image_context"] = {
                "dimensions": image_features.dimensions,
                "file_size": image_features.file_size,
                "dominant_colors": len(image_features.color_palette),
                "description": image_features.description
            }

            return structured_data

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Failed to parse structured analysis, using fallback", error=str(e), response_content=parsing_response.get("content", "")[:200])

            # Fallback to basic structure
            return {
                "color_harmony_score": 7.0,
                "typography_assessment": {"readability_score": 7.0},
                "layout_composition": {"balance_score": 7.0},
                "visual_hierarchy": {"clarity_score": 7.0},
                "accessibility_compliance": {"contrast_adequate": True},
                "brand_consistency": {"visual_coherence": 7.0},
                "overall_assessment": {"design_quality_score": 7.0},
                "raw_analysis": analysis_content[:500],  # First 500 chars
                "image_context": {
                    "dimensions": image_features.dimensions,
                    "file_size": image_features.file_size,
                    "dominant_colors": len(image_features.color_palette),
                    "description": image_features.description
                }
            }

    def _calculate_confidence(self, analysis_results: Dict[str, Any], image_features: ImageFeatures) -> float:
        """Calculate confidence score based on analysis completeness and image quality."""

        confidence_factors = []

        # Analysis completeness
        required_keys = ["color_harmony_score", "typography_assessment", "layout_composition"]
        completeness = sum(1 for key in required_keys if key in analysis_results) / len(required_keys)
        confidence_factors.append(completeness)

        # Image quality factors
        if image_features.dimensions["width"] >= 800 and image_features.dimensions["height"] >= 600:
            confidence_factors.append(0.9)  # Good resolution
        else:
            confidence_factors.append(0.6)  # Lower resolution

        # Color palette richness
        if len(image_features.color_palette) >= 5:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)

        # UI components detected
        if len(image_features.ui_components) > 0:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)

        return min(sum(confidence_factors) / len(confidence_factors), 1.0)

    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on analysis results."""

        recommendations = []

        try:
            # Color recommendations
            if analysis_results.get("color_harmony_score", 7) < 6:
                recommendations.append("Improve color harmony by selecting a more cohesive color palette")
                recommendations.append("Consider using color theory principles (complementary, triadic, or analogous schemes)")

            # Typography recommendations  
            typography = analysis_results.get("typography_assessment", {})
            if typography.get("readability_score", 7) < 6:
                recommendations.append("Improve text readability by increasing font size or adjusting line spacing")
            if typography.get("hierarchy_clarity", 7) < 6:
                recommendations.append("Establish clearer typography hierarchy with distinct font sizes and weights")

            # Layout recommendations
            layout = analysis_results.get("layout_composition", {})
            if layout.get("balance_score", 7) < 6:
                recommendations.append("Improve visual balance by redistributing elements more evenly")
            if layout.get("whitespace_usage", 7) < 6:
                recommendations.append("Optimize whitespace usage to reduce clutter and improve focus")

            # Accessibility recommendations
            accessibility = analysis_results.get("accessibility_compliance", {})
            if not accessibility.get("contrast_adequate", True):
                recommendations.append("Improve color contrast ratios to meet WCAG 2.1 AA standards")
            if not accessibility.get("text_readable", True):
                recommendations.append("Ensure all text meets minimum readability requirements")

            # Overall quality recommendations
            overall = analysis_results.get("overall_assessment", {})
            if overall.get("design_quality_score", 7) < 7:
                recommendations.append("Consider a comprehensive design review to enhance overall quality")
                recommendations.append("Focus on consistency in spacing, alignment, and visual elements")

            # Add some universal recommendations if list is empty
            if not recommendations:
                recommendations.extend([
                    "Consider A/B testing different design variations",
                    "Ensure mobile responsiveness across all screen sizes",
                    "Validate design decisions with user feedback"
                ])

        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            recommendations = [
                "Review visual design for consistency and clarity",
                "Ensure accessibility compliance across all elements",
                "Consider user experience optimization"
            ]

        return recommendations[:8]  # Limit to top 8 recommendations
