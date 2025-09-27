from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
import uuid
import base64

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed" 
    FAILED = "failed"

class AgentType(str, Enum):
    VISUAL_ANALYSIS = "visual_analysis"
    UX_CRITIQUE = "ux_critique"
    MARKET_RESEARCH = "market_research"
    TECHNICAL_FEASIBILITY = "technical_feasibility"
    BRAND_ALIGNMENT = "brand_alignment"

class ImageFeatures(BaseModel):
    """Extracted image features from processing pipeline."""
    clip_embeddings: List[float]
    description: str
    color_palette: List[Dict[str, Any]]
    layout_analysis: Dict[str, Any]
    text_elements: List[Dict[str, Any]]
    ui_components: List[Dict[str, Any]]
    dimensions: Dict[str, int]
    file_size: int
    
    def dict(self, **kwargs):
        """Override dict method to ensure proper serialization."""
        data = super().dict(**kwargs)
        # Ensure all values are JSON serializable
        for key, value in data.items():
            if hasattr(value, 'tolist'):  # numpy arrays
                data[key] = value.tolist()
            elif isinstance(value, bytes):
                data[key] = base64.b64encode(value).decode('utf-8')
        return data

class AnalysisRequest(BaseModel):
    """Request model for design analysis."""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_data: bytes
    image_features: Optional[ImageFeatures] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = Field(default_factory=dict)
    filename: Optional[str] = None
    analysis_types: List[AgentType] = Field(default=[
        AgentType.VISUAL_ANALYSIS,
        AgentType.UX_CRITIQUE,
        AgentType.MARKET_RESEARCH,
        AgentType.TECHNICAL_FEASIBILITY,
        AgentType.BRAND_ALIGNMENT
    ])

class AgentResult(BaseModel):
    """Result from individual agent analysis."""
    agent_type: AgentType
    status: AnalysisStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    analysis_results: Dict[str, Any]
    recommendations: List[str] = Field(default_factory=list)
    metrics: Dict[str, Union[int, float, str]] = Field(default_factory=dict)
    execution_time: float
    error_message: Optional[str] = None
    
    def dict(self, **kwargs):
        """Override dict method to ensure proper serialization."""
        data = super().dict(**kwargs)
        
        # Ensure analysis_results is JSON serializable
        if 'analysis_results' in data:
            serializable_results = {}
            for key, value in data['analysis_results'].items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    serializable_results[key] = value.isoformat()
                elif hasattr(value, 'tolist'):  # numpy arrays
                    serializable_results[key] = value.tolist()
                elif isinstance(value, bytes):
                    serializable_results[key] = base64.b64encode(value).decode('utf-8')
                else:
                    serializable_results[key] = value
            data['analysis_results'] = serializable_results
        
        return data

class AnalysisState(BaseModel):
    """State management for LangGraph workflow."""
    analysis_id: str
    status: AnalysisStatus
    uploaded_image: str  # Base64 encoded image data
    image_metadata: ImageFeatures
    analysis_results: Dict[AgentType, AgentResult] = Field(default_factory=dict)
    agent_outputs: List[Dict[str, Any]] = Field(default_factory=list)
    final_report: Optional[Dict[str, Any]] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_count: int = 0
    max_retries: int = 3
    
    def get_image_bytes(self) -> bytes:
        """Get the original image bytes from base64 encoded data."""
        return base64.b64decode(self.uploaded_image)
    
    @classmethod
    def create_with_image_bytes(cls, image_bytes: bytes, **kwargs) -> 'AnalysisState':
        """Create AnalysisState with image bytes (will be converted to base64)."""
        kwargs['uploaded_image'] = base64.b64encode(image_bytes).decode('utf-8')
        return cls(**kwargs)
    
    def dict(self, **kwargs):
        """Override dict method to ensure proper serialization."""
        data = super().dict(**kwargs)
        
        # Convert datetime objects to ISO format strings
        if 'started_at' in data and data['started_at']:
            data['started_at'] = data['started_at'].isoformat()
        if 'completed_at' in data and data['completed_at']:
            data['completed_at'] = data['completed_at'].isoformat()
        
        # Ensure all nested objects are properly serialized
        if 'analysis_results' in data:
            for key, value in data['analysis_results'].items():
                if hasattr(value, 'dict'):
                    data['analysis_results'][key] = value.dict()
        
        return data

class VisualAnalysisResult(BaseModel):
    """Specialized result for visual analysis agent."""
    color_harmony_score: float = Field(ge=0.0, le=10.0)
    typography_assessment: Dict[str, Any]
    layout_composition: Dict[str, Any] 
    visual_hierarchy: Dict[str, Any]
    accessibility_compliance: Dict[str, bool]
    brand_consistency: Dict[str, Any]
    improvement_suggestions: List[str]

class UXCritiqueResult(BaseModel):
    """Specialized result for UX critique agent."""
    usability_heuristics: Dict[str, Dict[str, Any]]
    user_journey_assessment: Dict[str, Any]
    information_architecture: Dict[str, Any]
    interaction_design: Dict[str, Any]
    accessibility_score: float = Field(ge=0.0, le=10.0)
    mobile_responsiveness: Dict[str, Any]
    wcag_compliance: Dict[str, bool]

class MarketResearchResult(BaseModel):
    """Specialized result for market research agent."""
    competitive_analysis: List[Dict[str, Any]]
    industry_trends: List[Dict[str, Any]]
    design_benchmarks: Dict[str, Any]
    target_audience_insights: Dict[str, Any]
    market_positioning: Dict[str, Any]
    pricing_strategy: Optional[Dict[str, Any]] = None

class TechnicalFeasibilityResult(BaseModel):
    """Specialized result for technical feasibility agent."""
    development_complexity: str = Field(pattern="^(low|medium|high|very_high)$")
    technology_recommendations: List[Dict[str, Any]]
    performance_considerations: Dict[str, Any]
    scalability_assessment: Dict[str, Any]
    security_considerations: List[str]
    implementation_timeline: Dict[str, Any]
    estimated_cost: Optional[Dict[str, Union[int, str]]] = None

class BrandAlignmentResult(BaseModel):
    """Specialized result for brand alignment agent."""
    brand_consistency_score: float = Field(ge=0.0, le=10.0)
    color_alignment: Dict[str, Any]
    typography_alignment: Dict[str, Any]
    visual_identity_strength: Dict[str, Any]
    brand_message_coherence: Dict[str, Any]
    logo_evaluation: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    """Complete analysis response."""
    analysis_id: str
    status: AnalysisStatus
    progress: float = Field(ge=0.0, le=100.0)
    visual_analysis: Optional[VisualAnalysisResult] = None
    ux_critique: Optional[UXCritiqueResult] = None
    market_research: Optional[MarketResearchResult] = None
    technical_feasibility: Optional[TechnicalFeasibilityResult] = None
    brand_alignment: Optional[BrandAlignmentResult] = None
    overall_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    key_recommendations: List[str] = Field(default_factory=list)
    improvement_roadmap: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None

class StreamingEvent(BaseModel):
    """Server-sent event for streaming responses."""
    event_type: str = Field(pattern="^(status|progress|result|error|complete)$")
    analysis_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    error_type: str
    analysis_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None

# Export all models
__all__ = [
    "AnalysisStatus", "AgentType", "ImageFeatures", "AnalysisRequest",
    "AgentResult", "AnalysisState", "VisualAnalysisResult", "UXCritiqueResult",
    "MarketResearchResult", "TechnicalFeasibilityResult", "BrandAlignmentResult",
    "AnalysisResponse", "StreamingEvent", "ErrorResponse"
]
