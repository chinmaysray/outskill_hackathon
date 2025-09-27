import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, Any, AsyncGenerator, Optional, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import structlog

from app.schemas.analysis import AnalysisRequest, AnalysisState, AnalysisStatus, StreamingEvent
from app.agents.visual_analysis.visual_analysis_agent import VisualAnalysisAgent
from app.agents.ux_critique.ux_critique_agent import UXCritiqueAgent
from app.agents.market_research.market_research_agent import MarketResearchAgent
from app.agents.technical_feasibility.technical_feasibility_agent import TechnicalFeasibilityAgent
from app.agents.brand_alignment.brand_alignment_agent import BrandAlignmentAgent
from app.utils.openrouter_client import OpenRouterClient

logger = structlog.get_logger(__name__)

class AnalysisOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent design analysis.
    Manages the workflow of specialized agents and streams results.
    """

    def __init__(self):
        self.agents = {}
        self.workflow = None
        self.memory_saver = MemorySaver()
        self.active_analyses: Dict[str, AnalysisState] = {}
        self.openrouter_client = None

    async def initialize(self):
        """Initialize all agents and create the workflow graph."""
        try:
            logger.info("Initializing Analysis Orchestrator")

            # Initialize OpenRouter client
            self.openrouter_client = OpenRouterClient()
            await self.openrouter_client.initialize()

            # Initialize all agents
            self.agents = {
                "visual_analysis": VisualAnalysisAgent(self.openrouter_client),
                "ux_critique": UXCritiqueAgent(self.openrouter_client), 
                "market_research": MarketResearchAgent(self.openrouter_client),
                "technical_feasibility": TechnicalFeasibilityAgent(self.openrouter_client),
                "brand_alignment": BrandAlignmentAgent(self.openrouter_client)
            }

            # Initialize all agents
            for agent_name, agent in self.agents.items():
                await agent.initialize()
                logger.info(f"Initialized {agent_name} agent")

            # Create workflow
            self._create_workflow()

            logger.info("Analysis Orchestrator initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize orchestrator", error=str(e))
            raise

    def is_healthy(self) -> bool:
        """Check if orchestrator is healthy."""
        return (
            self.workflow is not None and 
            all(agent.is_healthy() for agent in self.agents.values())
        )

    async def cleanup(self):
        """Cleanup all agents and resources."""
        logger.info("Cleaning up Analysis Orchestrator")
        for agent in self.agents.values():
            await agent.cleanup()
        if self.openrouter_client:
            await self.openrouter_client.cleanup()

    def _create_workflow(self):
        """Create the LangGraph workflow for multi-agent analysis."""

        # Define the workflow graph
        workflow = StateGraph(AnalysisState)

        # Add nodes for each processing step
        workflow.add_node("image_processor", self._process_image_node)
        workflow.add_node("visual_analysis", self._visual_analysis_node)
        workflow.add_node("ux_critique", self._ux_critique_node) 
        workflow.add_node("market_research", self._market_research_node)
        workflow.add_node("technical_feasibility", self._technical_feasibility_node)
        workflow.add_node("brand_alignment", self._brand_alignment_node)
        workflow.add_node("report_generator", self._generate_report_node)

        # Define the workflow edges
        workflow.set_entry_point("image_processor")

        # After image processing, route to all agents sequentially for now
        # TODO: Implement proper parallel execution
        workflow.add_edge("image_processor", "visual_analysis")
        workflow.add_edge("visual_analysis", "ux_critique")
        workflow.add_edge("ux_critique", "market_research")
        workflow.add_edge("market_research", "technical_feasibility")
        workflow.add_edge("technical_feasibility", "brand_alignment")
        workflow.add_edge("brand_alignment", "report_generator")

        # End after report generation
        workflow.add_edge("report_generator", END)

        # Compile the workflow without checkpointing to avoid serialization issues
        # TODO: Re-enable checkpointing once serialization issues are resolved
        self.workflow = workflow.compile()

        logger.info("Workflow graph created successfully")

    async def stream_analysis(self, request: AnalysisRequest) -> AsyncGenerator[str, None]:
        """
        Stream analysis results as Server-Sent Events.

        Args:
            request: Analysis request containing image and preferences

        Yields:
            str: SSE-formatted events with analysis progress and results
        """
        analysis_id = request.analysis_id

        try:
            # Initialize analysis state
            initial_state = AnalysisState.create_with_image_bytes(
                image_bytes=request.image_data,
                analysis_id=analysis_id,
                status=AnalysisStatus.PROCESSING,
                image_metadata=request.image_features,
                user_preferences=request.user_preferences,
                brand_guidelines=request.brand_guidelines,
                started_at=datetime.utcnow()
            )

            # Store in active analyses
            self.active_analyses[analysis_id] = initial_state

            # Send initial event
            yield self._format_sse_event(StreamingEvent(
                event_type="status",
                analysis_id=analysis_id,
                data={"status": "started", "message": "Analysis initiated"}
            ))

            # Run the workflow with streaming updates
            config = {"configurable": {"thread_id": analysis_id}}

            logger.info("Starting workflow execution", analysis_id=analysis_id)
            logger.info("Initial state dict", analysis_id=analysis_id, state_keys=list(initial_state.dict().keys()))
            async for event in self.workflow.astream(initial_state.dict(), config=config):
                logger.info("Workflow event received", analysis_id=analysis_id, event_keys=list(event.keys()))
                # Process workflow events and convert to SSE
                if "visual_analysis" in event:
                    visual_result = list(event.values())[0]
                    logger.info("Visual analysis completed", analysis_id=analysis_id, result_type=type(visual_result))
                    
                    logger.info("Yielding visual analysis progress event", analysis_id=analysis_id)
                    yield self._format_sse_event(StreamingEvent(
                        event_type="progress", 
                        analysis_id=analysis_id,
                        data={"stage": "visual_analysis", "progress": 20}
                    ))
                    
                    logger.info("Yielding visual analysis result event", analysis_id=analysis_id)
                    yield self._format_sse_event(StreamingEvent(
                        event_type="result",
                        analysis_id=analysis_id,
                        data={"agent": "visual_analysis", "result": visual_result}
                    ))

                elif "ux_critique" in event:
                    ux_result = list(event.values())[0]
                    logger.info("UX critique completed", analysis_id=analysis_id, result_type=type(ux_result))
                    
                    logger.info("Yielding UX critique progress event", analysis_id=analysis_id)
                    yield self._format_sse_event(StreamingEvent(
                        event_type="progress",
                        analysis_id=analysis_id, 
                        data={"stage": "ux_critique", "progress": 40}
                    ))
                    
                    logger.info("Yielding UX critique result event", analysis_id=analysis_id)
                    yield self._format_sse_event(StreamingEvent(
                        event_type="result",
                        analysis_id=analysis_id,
                        data={"agent": "ux_critique", "result": ux_result}
                    ))

                elif "market_research" in event:
                    market_result = list(event.values())[0]
                    logger.info("Market research completed", analysis_id=analysis_id, result_type=type(market_result))
                    
                    yield self._format_sse_event(StreamingEvent(
                        event_type="progress",
                        analysis_id=analysis_id,
                        data={"stage": "market_research", "progress": 60}
                    ))
                    
                    yield self._format_sse_event(StreamingEvent(
                        event_type="result",
                        analysis_id=analysis_id,
                        data={"agent": "market_research", "result": market_result}
                    ))

                elif "technical_feasibility" in event:
                    tech_result = list(event.values())[0]
                    logger.info("Technical feasibility completed", analysis_id=analysis_id, result_type=type(tech_result))
                    
                    yield self._format_sse_event(StreamingEvent(
                        event_type="progress",
                        analysis_id=analysis_id,
                        data={"stage": "technical_feasibility", "progress": 80}
                    ))
                    
                    yield self._format_sse_event(StreamingEvent(
                        event_type="result",
                        analysis_id=analysis_id,
                        data={"agent": "technical_feasibility", "result": tech_result}
                    ))

                elif "brand_alignment" in event:
                    brand_result = list(event.values())[0]
                    logger.info("Brand alignment completed", analysis_id=analysis_id, result_type=type(brand_result))
                    
                    yield self._format_sse_event(StreamingEvent(
                        event_type="progress",
                        analysis_id=analysis_id,
                        data={"stage": "brand_alignment", "progress": 90}
                    ))
                    
                    yield self._format_sse_event(StreamingEvent(
                        event_type="result",
                        analysis_id=analysis_id,
                        data={"agent": "brand_alignment", "result": brand_result}
                    ))

                elif "report_generator" in event:
                    # Final results
                    # Log without image data and embeddings to avoid cluttering logs
                    event_data_clean = {}
                    for k, v in event.items():
                        if isinstance(v, dict):
                            cleaned_v = {}
                            for key, value in v.items():
                                if key == 'uploaded_image':
                                    cleaned_v[key] = f'[IMAGE_DATA_{len(value)}chars]'
                                elif key == 'image_metadata' and isinstance(value, dict):
                                    # Clean image metadata, especially embeddings
                                    cleaned_metadata = {**value}
                                    if 'clip_embeddings' in cleaned_metadata:
                                        cleaned_metadata['clip_embeddings'] = f'[EMBEDDINGS_{len(cleaned_metadata["clip_embeddings"])}values]'
                                    cleaned_v[key] = cleaned_metadata
                                else:
                                    cleaned_v[key] = value
                            event_data_clean[k] = cleaned_v
                        else:
                            event_data_clean[k] = v
                    logger.info("Report generator event received", analysis_id=analysis_id, event_data=event_data_clean)
                    final_state_dict = list(event.values())[0]
                    # Log state info without image data and embeddings
                    state_info = {
                        'state_type': type(final_state_dict),
                        'state_keys': list(final_state_dict.keys()) if isinstance(final_state_dict, dict) else "Not a dict",
                        'image_size': len(final_state_dict.get('uploaded_image', '')) if isinstance(final_state_dict, dict) else 0
                    }
                    if isinstance(final_state_dict, dict) and 'image_metadata' in final_state_dict:
                        metadata = final_state_dict['image_metadata']
                        if isinstance(metadata, dict) and 'clip_embeddings' in metadata:
                            state_info['embeddings_count'] = len(metadata['clip_embeddings'])
                    logger.info("Final state dict extracted", analysis_id=analysis_id, **state_info)
                    
                    # Convert back to AnalysisState object for proper attribute access
                    try:
                        final_state = AnalysisState(**final_state_dict)
                        logger.info("AnalysisState object created successfully", analysis_id=analysis_id, has_final_report=hasattr(final_state, 'final_report'))
                        self.active_analyses[analysis_id] = final_state

                        logger.info("Yielding complete event", analysis_id=analysis_id)
                        yield self._format_sse_event(StreamingEvent(
                            event_type="complete",
                            analysis_id=analysis_id,
                            data={
                                "status": "completed",
                                "progress": 100,
                                "results": final_state.final_report
                            }
                        ))
                    except Exception as e:
                        logger.error("Failed to create AnalysisState object", analysis_id=analysis_id, error=str(e), final_state_dict=final_state_dict)
                        raise

        except Exception as e:
            import traceback
            logger.error("Analysis failed", analysis_id=analysis_id, error=str(e), traceback=traceback.format_exc())

            # Update state with error
            if analysis_id in self.active_analyses:
                analysis_state = self.active_analyses[analysis_id]
                logger.info("Updating analysis state with error", analysis_id=analysis_id, state_type=type(analysis_state))
                if isinstance(analysis_state, dict):
                    # Handle case where it's stored as a dictionary
                    logger.info("Setting status on dict object", analysis_id=analysis_id)
                    analysis_state['status'] = AnalysisStatus.FAILED
                else:
                    # Handle case where it's an AnalysisState object
                    logger.info("Setting status on AnalysisState object", analysis_id=analysis_id)
                    analysis_state.status = AnalysisStatus.FAILED
            else:
                logger.warning("Analysis ID not found in active analyses", analysis_id=analysis_id, active_analyses_keys=list(self.active_analyses.keys()))

            yield self._format_sse_event(StreamingEvent(
                event_type="error",
                analysis_id=analysis_id,
                data={"error": str(e), "status": "failed"}
            ))

    async def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an analysis."""
        if analysis_id not in self.active_analyses:
            return None

        state = self.active_analyses[analysis_id]
        return {
            "analysis_id": analysis_id,
            "status": state.status,
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None,
            "progress": self._calculate_progress(state)
        }

    async def get_analysis_report(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get completed analysis report."""
        if analysis_id not in self.active_analyses:
            return None

        state = self.active_analyses[analysis_id]
        if state.status != AnalysisStatus.COMPLETED:
            return None

        return state.final_report

    # Node implementations
    async def _process_image_node(self, state: AnalysisState) -> Dict[str, Any]:
        """Process the uploaded image."""
        logger.info("Processing image", analysis_id=state.analysis_id)
        try:
            # Test serialization of state
            test_dict = state.dict()
            logger.info("State serialization successful", analysis_id=state.analysis_id)
        except Exception as e:
            logger.error("State serialization failed", analysis_id=state.analysis_id, error=str(e))
            raise
        # Image processing already done in the main app
        return state.dict()

    async def _visual_analysis_node(self, state: AnalysisState) -> Dict[str, Any]:
        """Run visual analysis agent."""
        try:
            result = await self.agents["visual_analysis"].analyze(
                state.get_image_bytes(),
                state.image_metadata,
                state.user_preferences
            )
            state.analysis_results["visual_analysis"] = result
            state.agent_outputs.append({"agent": "visual_analysis", "result": result.dict()})
            return state.dict()
        except Exception as e:
            logger.error("Visual analysis failed", error=str(e))
            state.error_count += 1
            return state.dict()

    async def _ux_critique_node(self, state: AnalysisState) -> Dict[str, Any]:
        """Run UX critique agent."""
        try:
            result = await self.agents["ux_critique"].analyze(
                state.get_image_bytes(),
                state.image_metadata,
                state.user_preferences
            )
            state.analysis_results["ux_critique"] = result
            state.agent_outputs.append({"agent": "ux_critique", "result": result.dict()})
            return state.dict()
        except Exception as e:
            logger.error("UX critique failed", error=str(e))
            state.error_count += 1
            return state.dict()

    async def _market_research_node(self, state: AnalysisState) -> Dict[str, Any]:
        """Run market research agent."""
        try:
            result = await self.agents["market_research"].analyze(
                state.get_image_bytes(),
                state.image_metadata,
                state.user_preferences
            )
            state.analysis_results["market_research"] = result
            state.agent_outputs.append({"agent": "market_research", "result": result.dict()})
            return state.dict()
        except Exception as e:
            logger.error("Market research failed", error=str(e))
            state.error_count += 1
            return state.dict()

    async def _technical_feasibility_node(self, state: AnalysisState) -> Dict[str, Any]:
        """Run technical feasibility agent."""
        try:
            result = await self.agents["technical_feasibility"].analyze(
                state.get_image_bytes(),
                state.image_metadata,
                state.user_preferences
            )
            state.analysis_results["technical_feasibility"] = result
            state.agent_outputs.append({"agent": "technical_feasibility", "result": result.dict()})
            return state.dict()
        except Exception as e:
            logger.error("Technical feasibility analysis failed", error=str(e))
            state.error_count += 1
            return state.dict()

    async def _brand_alignment_node(self, state: AnalysisState) -> Dict[str, Any]:
        """Run brand alignment agent."""
        try:
            result = await self.agents["brand_alignment"].analyze(
                state.get_image_bytes(),
                state.image_metadata,
                state.brand_guidelines
            )
            state.analysis_results["brand_alignment"] = result
            state.agent_outputs.append({"agent": "brand_alignment", "result": result.dict()})
            return state.dict()
        except Exception as e:
            logger.error("Brand alignment analysis failed", error=str(e))
            state.error_count += 1
            return state.dict()

    async def _generate_report_node(self, state: AnalysisState) -> Dict[str, Any]:
        """Generate final analysis report."""
        try:
            logger.info("Generating final report", analysis_id=state.analysis_id)

            # Aggregate all results
            report = {
                "analysis_id": state.analysis_id,
                "summary": {
                    "total_agents": len(state.analysis_results),
                    "successful_analyses": len([r for r in state.analysis_results.values() 
                                              if r.status == AnalysisStatus.COMPLETED]),
                    "overall_confidence": sum([r.confidence_score for r in state.analysis_results.values()]) / max(len(state.analysis_results), 1)
                },
                "results": {k: v.dict() for k, v in state.analysis_results.items()},
                "recommendations": self._generate_recommendations(state),
                "improvement_roadmap": self._generate_roadmap(state),
                "generated_at": datetime.utcnow().isoformat()
            }

            state.final_report = report
            state.status = AnalysisStatus.COMPLETED
            state.completed_at = datetime.utcnow()

            return state.dict()

        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            state.status = AnalysisStatus.FAILED
            state.error_count += 1
            return state.dict()

    def _generate_recommendations(self, state: AnalysisState) -> List[str]:
        """Generate key recommendations from all agent results."""
        recommendations = []

        for result in state.analysis_results.values():
            recommendations.extend(result.recommendations)

        # Deduplicate and prioritize
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:10]  # Top 10 recommendations

    def _generate_roadmap(self, state: AnalysisState) -> List[Dict[str, Any]]:
        """Generate improvement roadmap."""
        roadmap = [
            {
                "phase": "Quick Wins", 
                "duration": "1-2 weeks",
                "items": ["Color contrast improvements", "Typography fixes", "Basic layout adjustments"]
            },
            {
                "phase": "Medium-term Improvements",
                "duration": "1-2 months", 
                "items": ["UX flow optimization", "Component redesign", "Brand alignment updates"]
            },
            {
                "phase": "Long-term Strategy",
                "duration": "3-6 months",
                "items": ["Complete redesign consideration", "Advanced functionality", "Market positioning"]
            }
        ]
        return roadmap

    def _calculate_progress(self, state: AnalysisState) -> float:
        """Calculate analysis progress percentage."""
        total_agents = 5
        completed_agents = len([r for r in state.analysis_results.values() 
                              if r.status == AnalysisStatus.COMPLETED])
        return (completed_agents / total_agents) * 100

    def _format_sse_event(self, event: StreamingEvent) -> str:
        """Format event as Server-Sent Event."""
        def json_serializer(obj):
            """Custom JSON serializer for various object types."""
            import numpy as np
            
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, bytes):
                return base64.b64encode(obj).decode('utf-8')
            elif hasattr(obj, 'dict'):
                return obj.dict()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        formatted_event = f"event: {event.event_type}\ndata: {json.dumps(event.dict(), default=json_serializer)}\n\n"
        logger.info("Sending SSE event to client", event_type=event.event_type, analysis_id=event.analysis_id)
        return formatted_event
