export interface UploadState {
  isDragActive: boolean
  isDragReject: boolean
  isDragAccept: boolean
  selectedFile: File | null
  uploadProgress: number
  error?: string
}

export interface AnalysisState {
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  startTime?: Date
  endTime?: Date
  results?: AnalysisResults
  error?: string
}

export interface AnalysisResults {
  analysis_id?: string
  summary?: {
    total_agents: number
    successful_analyses: number
    overall_confidence: number
  }
  results?: {
    visual_analysis?: AgentResult
    ux_critique?: AgentResult
    market_research?: AgentResult
    technical_feasibility?: AgentResult
    brand_alignment?: AgentResult
  }
  recommendations?: string[]
  improvement_roadmap?: any[]
  generated_at?: string
  // Legacy support for flat structure
  visual_analysis?: AgentResult
  ux_critique?: AgentResult
  market_research?: AgentResult
  technical_feasibility?: AgentResult
  brand_alignment?: AgentResult
}

export interface AgentResult {
  agent_type: string
  status: 'completed' | 'processing' | 'pending' | 'error'
  confidence_score: number
  analysis_results: Record<string, any>
  recommendations: string[]
  metrics: Record<string, any>
  execution_time: number
  error_message?: string
}

export interface AnalysisRequest {
  image: File
  user_preferences: {
    industry: string
    target_audience: string[]
  }
}

export interface AnalysisResponse {
  request_id: string
  status: 'processing' | 'completed' | 'error'
  results?: AnalysisResults
  error?: string
}

export interface StreamingEvent {
  event_type: 'status' | 'progress' | 'result' | 'error' | 'complete'
  data: any
  timestamp: Date
}

export interface APIError {
  message: string
  code: string
  details?: any
}

export type AgentType = 
  | 'visual_analysis' 
  | 'ux_critique' 
  | 'market_research' 
  | 'technical_feasibility' 
  | 'brand_alignment'
