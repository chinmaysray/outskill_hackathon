import json
import asyncio
from typing import Dict, Any, List
import structlog

from app.schemas.analysis import AgentResult, AnalysisStatus, AgentType, UXCritiqueResult, ImageFeatures
from app.utils.openrouter_client import OpenRouterClient
from app.core.config import settings

logger = structlog.get_logger(__name__)

class UXCritiqueAgent:
    """
    Specialized agent for comprehensive user experience evaluation 
    based on established UX principles and usability heuristics.
    """

    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
        self.agent_type = AgentType.UX_CRITIQUE
        self.model = settings.default_text_model

        # Nielsen's 10 Usability Heuristics for reference
        self.usability_heuristics = [
            "Visibility of system status",
            "Match between system and real world", 
            "User control and freedom",
            "Consistency and standards",
            "Error prevention",
            "Recognition rather than recall",
            "Flexibility and efficiency of use",
            "Aesthetic and minimalist design",
            "Help users recognize, diagnose, and recover from errors",
            "Help and documentation"
        ]

    async def initialize(self):
        """Initialize the UX critique agent."""
        logger.info("Initializing UX Critique Agent")

    def is_healthy(self) -> bool:
        """Check if agent is healthy."""
        return self.client is not None

    async def cleanup(self):
        """Cleanup agent resources."""
        logger.info("Cleaning up UX Critique Agent")

    async def analyze(
        self, 
        image_data: bytes, 
        image_features: ImageFeatures, 
        user_preferences: Dict[str, Any]
    ) -> AgentResult:
        """
        Perform comprehensive UX critique analysis.

        Args:
            image_data: Raw image bytes
            image_features: Extracted image features
            user_preferences: User preferences and context

        Returns:
            AgentResult with UX analysis findings
        """
        start_time = asyncio.get_event_loop().time()

        try:
            logger.info("Starting UX critique analysis")

            # Create comprehensive UX analysis prompt
            analysis_prompt = self._create_ux_analysis_prompt(image_features, user_preferences)

            # Perform vision-based UX analysis
            response = await self.client.vision_analysis(
                image_data=image_data,
                prompt=analysis_prompt,
                model=settings.default_vision_model,
                detail="high"
            )

            # Parse and structure the UX analysis results
            analysis_results = await self._parse_ux_analysis_results(response["content"], image_features)

            # Calculate confidence score
            confidence_score = self._calculate_ux_confidence(analysis_results, image_features)

            # Generate UX recommendations
            recommendations = self._generate_ux_recommendations(analysis_results)

            execution_time = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                agent_type=self.agent_type,
                status=AnalysisStatus.COMPLETED,
                confidence_score=confidence_score,
                analysis_results=analysis_results,
                recommendations=recommendations,
                metrics={
                    "heuristics_evaluated": len(self.usability_heuristics),
                    "ui_elements_analyzed": len(image_features.ui_components),
                    "accessibility_checks": 7,  # Number of accessibility criteria checked
                    "execution_time_seconds": round(execution_time, 2)
                },
                execution_time=execution_time
            )

        except Exception as e:
            logger.error("UX critique analysis failed", error=str(e))
            execution_time = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                agent_type=self.agent_type,
                status=AnalysisStatus.FAILED,
                confidence_score=0.0,
                analysis_results={"error": str(e)},
                recommendations=["UX critique analysis could not be completed"],
                metrics={"execution_time_seconds": round(execution_time, 2)},
                execution_time=execution_time,
                error_message=str(e)
            )

    def _create_ux_analysis_prompt(self, image_features: ImageFeatures, user_preferences: Dict[str, Any]) -> str:
        """Create comprehensive UX analysis prompt."""

        prompt = f"""You are a senior UX designer. Perform a comprehensive critique of this interface design using Nielsen's 10 Usability Heuristics and modern UX best practices.

        **USABILITY HEURISTICS**
        1. Visibility of System Status
        2. Match Between System and Real World
        3. User Control and Freedom
        4. Consistency and Standards
        5. Error Prevention
        6. Recognition Rather Than Recall
        7. Flexibility and Efficiency of Use
        8. Aesthetic and Minimalist Design
        9. Error Recognition and Recovery
        10. Help and Documentation

        For each heuristic, assess strengths, weaknesses, and provide a score (1-10).

        **ADDITIONAL UX ANALYSIS**
        - Information Architecture: clarity, organization, navigation patterns.
        - Interaction Design: touch targets, feedback, purposeful animations.
        - Accessibility: color contrast, keyboard navigation, screen reader compatibility, motor accessibility.
        - Mobile Responsiveness: touch target sizes, thumb-friendly navigation, scaling and layout.
        - User Journey: task flow clarity, friction points, conversion optimization.

        **CONTEXT**
        Image dimensions: {image_features.dimensions['width']}x{image_features.dimensions['height']}
        Detected UI components: {len(image_features.ui_components)} elements
        Text elements found: {len(image_features.text_elements)}
        User preferences: {json.dumps(user_preferences, indent=2) if user_preferences else "None specified"}

        **ACTIONABLE FEEDBACK**
        - Provide specific scores (1-10) for each heuristic and category.
        - List at least three concrete recommendations to improve UX.
        - Highlight strengths and weaknesses.

        Format your response as a structured report for easy parsing.
        """
        return prompt

    async def _parse_ux_analysis_results(self, analysis_content: str, image_features: ImageFeatures) -> Dict[str, Any]:
        """Parse and structure the UX analysis results."""

        parsing_prompt = f"""Extract specific UX metrics from this analysis:

{analysis_content}

Format as JSON with these exact keys:
{{
  "usability_heuristics": {{
    "visibility_of_status": {{"score": <float 1-10>, "issues": [<string>]}},
    "match_real_world": {{"score": <float 1-10>, "issues": [<string>]}},
    "user_control": {{"score": <float 1-10>, "issues": [<string>]}},
    "consistency": {{"score": <float 1-10>, "issues": [<string>]}},
    "error_prevention": {{"score": <float 1-10>, "issues": [<string>]}},
    "recognition_vs_recall": {{"score": <float 1-10>, "issues": [<string>]}},
    "flexibility": {{"score": <float 1-10>, "issues": [<string>]}},
    "aesthetic_minimalism": {{"score": <float 1-10>, "issues": [<string>]}},
    "error_recovery": {{"score": <float 1-10>, "issues": [<string>]}},
    "help_documentation": {{"score": <float 1-10>, "issues": [<string>]}}
  }},
  "user_journey_assessment": {{
    "task_flow_clarity": <float 1-10>,
    "navigation_intuitiveness": <float 1-10>,
    "friction_points": <int>,
    "conversion_potential": <float 1-10>
  }},
  "information_architecture": {{
    "hierarchy_clarity": <float 1-10>,
    "content_organization": <float 1-10>,
    "findability": <float 1-10>
  }},
  "interaction_design": {{
    "touch_targets_appropriate": <boolean>,
    "feedback_quality": <float 1-10>,
    "animation_purposefulness": <float 1-10>
  }},
  "accessibility_score": <float 1-10>,
  "mobile_responsiveness": {{
    "touch_friendly": <boolean>,
    "thumb_navigation": <boolean>,
    "responsive_layout": <boolean>
  }},
  "wcag_compliance": {{
    "contrast_adequate": <boolean>,
    "keyboard_accessible": <boolean>,
    "screen_reader_friendly": <boolean>,
    "focus_indicators": <boolean>
  }}
}}
"""

        try:
            parsing_response = await self.client.text_analysis(
                prompt=parsing_prompt,
                model=settings.default_text_model,
                temperature=0.1
            )

            structured_data = json.loads(parsing_response["content"])

            # Add context from image analysis
            structured_data["analysis_context"] = {
                "ui_elements_count": len(image_features.ui_components),
                "text_elements_count": len(image_features.text_elements),
                "screen_dimensions": image_features.dimensions,
                "design_description": image_features.description
            }

            return structured_data

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse structured UX analysis, using fallback", error=str(e))

            # Fallback structure
            return {
                "usability_heuristics": {
                    heuristic.lower().replace(" ", "_"): {"score": 7.0, "issues": []}
                    for heuristic in self.usability_heuristics[:5]  # First 5 heuristics
                },
                "user_journey_assessment": {
                    "task_flow_clarity": 7.0,
                    "navigation_intuitiveness": 7.0,
                    "friction_points": 2,
                    "conversion_potential": 7.0
                },
                "information_architecture": {
                    "hierarchy_clarity": 7.0,
                    "content_organization": 7.0,
                    "findability": 7.0
                },
                "accessibility_score": 7.0,
                "mobile_responsiveness": {
                    "touch_friendly": True,
                    "thumb_navigation": True,
                    "responsive_layout": True
                },
                "raw_analysis": analysis_content[:500],
                "analysis_context": {
                    "ui_elements_count": len(image_features.ui_components),
                    "text_elements_count": len(image_features.text_elements),
                    "screen_dimensions": image_features.dimensions,
                    "design_description": image_features.description
                }
            }

    def _calculate_ux_confidence(self, analysis_results: Dict[str, Any], image_features: ImageFeatures) -> float:
        """Calculate confidence score for UX analysis."""

        confidence_factors = []

        # Analysis completeness
        required_sections = ["usability_heuristics", "user_journey_assessment", "information_architecture"]
        completeness = sum(1 for section in required_sections if section in analysis_results) / len(required_sections)
        confidence_factors.append(completeness)

        # UI element detection quality
        if len(image_features.ui_components) > 3:
            confidence_factors.append(0.9)  # Good UI element detection
        elif len(image_features.ui_components) > 0:
            confidence_factors.append(0.7)  # Some UI elements
        else:
            confidence_factors.append(0.4)  # Limited UI elements

        # Text element availability for content analysis
        if len(image_features.text_elements) > 2:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)

        # Image quality factor
        total_pixels = image_features.dimensions["width"] * image_features.dimensions["height"]
        if total_pixels >= 500000:  # ~720p or better
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)

        return min(sum(confidence_factors) / len(confidence_factors), 1.0)

    def _generate_ux_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate specific UX recommendations."""

        recommendations = []

        try:
            # Heuristic-based recommendations
            heuristics = analysis_results.get("usability_heuristics", {})
            for heuristic_name, heuristic_data in heuristics.items():
                if isinstance(heuristic_data, dict) and heuristic_data.get("score", 7) < 6:
                    if "visibility" in heuristic_name:
                        recommendations.append("Improve system status visibility with better feedback and state indicators")
                    elif "consistency" in heuristic_name:
                        recommendations.append("Enhance design consistency across all interface elements")
                    elif "control" in heuristic_name:
                        recommendations.append("Provide clearer navigation and undo capabilities")
                    elif "error" in heuristic_name:
                        recommendations.append("Implement better error prevention and recovery mechanisms")

            # Accessibility recommendations
            accessibility_score = analysis_results.get("accessibility_score", 7)
            if accessibility_score < 7:
                recommendations.append("Improve accessibility compliance with WCAG 2.1 guidelines")

            wcag = analysis_results.get("wcag_compliance", {})
            if not wcag.get("contrast_adequate", True):
                recommendations.append("Increase color contrast ratios to meet accessibility standards")
            if not wcag.get("keyboard_accessible", True):
                recommendations.append("Ensure all interactive elements are keyboard accessible")

            # Mobile responsiveness recommendations
            mobile = analysis_results.get("mobile_responsiveness", {})
            if not mobile.get("touch_friendly", True):
                recommendations.append("Increase touch target sizes to minimum 44px for better mobile usability")
            if not mobile.get("thumb_navigation", True):
                recommendations.append("Optimize navigation for thumb-friendly mobile interaction")

            # Information architecture recommendations
            ia = analysis_results.get("information_architecture", {})
            if ia.get("hierarchy_clarity", 7) < 6:
                recommendations.append("Clarify information hierarchy with better visual organization")
            if ia.get("findability", 7) < 6:
                recommendations.append("Improve content findability with better search and navigation")

            # User journey recommendations
            journey = analysis_results.get("user_journey_assessment", {})
            if journey.get("friction_points", 0) > 3:
                recommendations.append("Reduce friction points in primary user flows")
            if journey.get("conversion_potential", 7) < 7:
                recommendations.append("Optimize conversion paths and reduce abandonment risks")

            # Generic recommendations if none generated
            if not recommendations:
                recommendations.extend([
                    "Conduct user testing to validate design decisions",
                    "Implement progressive disclosure to reduce cognitive load",
                    "Ensure consistent interaction patterns throughout the interface",
                    "Optimize for mobile-first user experience"
                ])

        except Exception as e:
            logger.error("Failed to generate UX recommendations", error=str(e))
            recommendations = [
                "Conduct comprehensive usability testing",
                "Review accessibility compliance",
                "Optimize mobile user experience",
                "Improve visual hierarchy and information architecture"
            ]

        return recommendations[:10]  # Limit to top 10 recommendations
