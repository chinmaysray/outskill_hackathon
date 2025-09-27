'use client'

import React, { useState, useEffect } from 'react'
import { 
  Box, 
  Grid, 
  Paper, 
  Typography, 
  LinearProgress, 
  Chip,
  Card,
  CardContent,
  Alert,
  Stack,
  Fade,
  Slide,
  Zoom,
  Skeleton,
  useTheme,
  alpha,
  keyframes
} from '@mui/material'
import { 
  Assessment, 
  Visibility, 
  Psychology, 
  TrendingUp, 
  Code, 
  Palette,
  CheckCircle,
  TrendingUp as TrendingUpIcon,
  Speed,
  Star,
  Timeline,
  AutoAwesome,
  Insights
} from '@mui/icons-material'
import { AnalysisState, AgentType } from '@/types/analysis'

interface AnalysisDashboardProps {
  analysisState: AnalysisState
}

// Premium animations
const shimmerAnimation = keyframes`
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
`

const pulseAnimation = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`

const slideInUp = keyframes`
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const floatingAnimation = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
`

const agentConfig: Record<AgentType, { 
  name: string; 
  icon: React.ElementType; 
  gradient: string;
  lightGradient: string;
  description: string;
  metrics: string[];
  accentColor: string;
}> = {
  visual_analysis: {
    name: 'Visual Analysis',
    icon: Visibility,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    lightGradient: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
    description: 'Analyzes visual elements, composition, and aesthetics',
    metrics: ['Color Harmony', 'Typography', 'Layout Balance'],
    accentColor: '#667eea'
  },
  ux_critique: {
    name: 'UX Critique',
    icon: Psychology,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    lightGradient: 'linear-gradient(135deg, rgba(240, 147, 251, 0.1) 0%, rgba(245, 87, 108, 0.1) 100%)',
    description: 'Evaluates user experience and usability patterns',
    metrics: ['Accessibility', 'Usability', 'Navigation Flow'],
    accentColor: '#f093fb'
  },
  market_research: {
    name: 'Market Research',
    icon: TrendingUp,
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    lightGradient: 'linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%)',
    description: 'Provides market insights and competitive analysis',
    metrics: ['Market Position', 'Trends', 'Competition'],
    accentColor: '#4facfe'
  },
  technical_feasibility: {
    name: 'Technical Feasibility',
    icon: Code,
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    lightGradient: 'linear-gradient(135deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.1) 100%)',
    description: 'Assesses technical implementation complexity',
    metrics: ['Complexity', 'Performance', 'Scalability'],
    accentColor: '#43e97b'
  },
  brand_alignment: {
    name: 'Brand Alignment',
    icon: Palette,
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    lightGradient: 'linear-gradient(135deg, rgba(250, 112, 154, 0.1) 0%, rgba(254, 225, 64, 0.1) 100%)',
    description: 'Evaluates brand consistency and alignment',
    metrics: ['Brand Consistency', 'Visual Identity', 'Message Coherence'],
    accentColor: '#fa709a'
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'primary'
    case 'error': return 'error'
    default: return 'default'
  }
}

function formatDuration(startTime?: Date, endTime?: Date): string {
  if (!startTime) return 'N/A'
  const end = endTime || new Date()
  const duration = end.getTime() - startTime.getTime()
  return `${(duration / 1000).toFixed(1)}s`
}

function AnalysisDashboard({ analysisState }: AnalysisDashboardProps) {
  const { status, progress, results, startTime, endTime, error } = analysisState
  const theme = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (status === 'pending') {
    return null
  }

  if (status === 'error') {
    return (
      <Fade in timeout={300}>
        <Alert 
          severity="error" 
          sx={{ 
            borderRadius: 4,
            background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 20px 40px rgba(239, 68, 68, 0.1)'
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
            Analysis Failed
          </Typography>
          <Typography variant="body2">
            {error}
          </Typography>
        </Alert>
      </Fade>
    )
  }

  return (
    <Box sx={{ 
      background: 'linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%)',
      borderRadius: 6,
      p: 4,
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      boxShadow: '0 25px 50px rgba(0, 0, 0, 0.1)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background decorative elements */}
      <Box sx={{ 
        position: 'absolute',
        top: -100,
        right: -100,
        width: 200,
        height: 200,
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, transparent 100%)',
        borderRadius: '50%',
        animation: `${floatingAnimation} 6s ease-in-out infinite`
      }} />
      <Box sx={{ 
        position: 'absolute',
        bottom: -50,
        left: -50,
        width: 150,
        height: 150,
        background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.1) 0%, transparent 100%)',
        borderRadius: '50%',
        animation: `${floatingAnimation} 8s ease-in-out infinite reverse`
      }} />

      {/* Header */}
      <Box sx={{ mb: 4, position: 'relative' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ 
            p: 2, 
            borderRadius: 4, 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            mr: 3,
            boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)'
          }}>
            <Assessment sx={{ color: 'white', fontSize: 32 }} />
          </Box>
          <Box>
            <Typography variant="h4" color="text.primary" sx={{ fontWeight: 800, mb: 0.5 }}>
              AI Analysis Dashboard
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400 }}>
              Comprehensive design insights powered by advanced AI
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Premium Progress Bar */}
      {status === 'processing' && (
        <Slide direction="down" in timeout={500}>
          <Box sx={{ mb: 6 }}>
            <Box sx={{ 
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%)',
              backdropFilter: 'blur(20px)',
              borderRadius: 4,
              p: 4,
              border: '1px solid rgba(255, 255, 255, 0.3)',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)'
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: 3, 
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    mr: 2,
                    animation: `${pulseAnimation} 2s infinite`
                  }}>
                    <Timeline sx={{ color: 'white', fontSize: 24 }} />
                  </Box>
                  <Box>
                    <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700 }}>
                      AI Analysis in Progress
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      5 specialized agents working on your design
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="h4" color="primary.main" sx={{ fontWeight: 700 }}>
                  {Math.round(progress)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ 
                  height: 12, 
                  borderRadius: 6,
                  backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 6,
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                    boxShadow: '0 4px 20px rgba(102, 126, 234, 0.4)'
                  }
                }}
              />
            </Box>
          </Box>
        </Slide>
      )}

      {/* Premium Summary Card */}
      {status === 'completed' && results && (
        <Zoom in={mounted} timeout={800}>
          <Box sx={{ 
            mb: 6,
            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)',
            borderRadius: 4,
            p: 4,
            border: '1px solid rgba(34, 197, 94, 0.2)',
            backdropFilter: 'blur(10px)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <Box sx={{ 
              position: 'absolute',
              top: -50,
              right: -50,
              width: 100,
              height: 100,
              background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, transparent 100%)',
              borderRadius: '50%'
            }} />
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <CheckCircle sx={{ color: 'success.main', fontSize: 32, mr: 2 }} />
              <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700 }}>
                Analysis Complete
              </Typography>
            </Box>
            <Grid container spacing={4}>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" color="primary.main" sx={{ fontWeight: 800 }}>
                    {Object.keys(results).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                    Specialized Agents
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" color="success.main" sx={{ fontWeight: 800 }}>
                    {results.summary ? Math.round((results.summary.overall_confidence || 0) * 100) : 85}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                    Overall Confidence
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" color="warning.main" sx={{ fontWeight: 800 }}>
                    {results.recommendations ? results.recommendations.length : 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                    Recommendations
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Zoom>
      )}

      {/* Premium Agent Cards */}
      <Grid container spacing={4}>
        {Object.entries(agentConfig).map(([agentType, config], index) => {
          const IconComponent = config.icon
          const result = results?.results?.[agentType as AgentType] || results?.[agentType as AgentType]
          const isCompleted = status === 'completed' && result
          const isProcessing = status === 'processing' && result?.status === 'processing'

          return (
            <Grid item xs={12} sm={6} lg={4} key={agentType}>
              <Fade in={mounted} timeout={600 + index * 200}>
                <Card 
                  sx={{ 
                    height: '100%',
                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                    cursor: 'pointer',
                    position: 'relative',
                    overflow: 'hidden',
                    background: isCompleted 
                      ? `linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%)`
                      : 'linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(248, 250, 252, 0.8) 100%)',
                    backdropFilter: 'blur(20px)',
                    border: isCompleted 
                      ? `2px solid transparent`
                      : '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: 4,
                    boxShadow: isCompleted 
                      ? '0 20px 40px rgba(0, 0, 0, 0.1)'
                      : '0 10px 30px rgba(0, 0, 0, 0.05)',
                    '&::before': isCompleted ? {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: config.gradient,
                      opacity: 0.05,
                      zIndex: -1
                    } : {},
                    '&:hover': {
                      transform: 'translateY(-8px) scale(1.02)',
                      boxShadow: '0 25px 50px rgba(0,0,0,0.15)',
                      '&::before': isCompleted ? {
                        opacity: 0.1
                      } : {}
                    }
                  }}
                >
                  <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
                    {/* Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                      <Box 
                        sx={{ 
                          p: 2, 
                          borderRadius: 3, 
                          background: isCompleted ? config.gradient : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
                          color: 'white',
                          mr: 3,
                          transition: 'all 0.3s ease',
                          boxShadow: isCompleted ? '0 8px 25px rgba(0,0,0,0.15)' : 'none'
                        }}
                      >
                        <IconComponent sx={{ fontSize: 28 }} />
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" color="text.primary" sx={{ fontWeight: 700, mb: 0.5 }}>
                          {config.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.4 }}>
                          {config.description}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Status */}
                    <Box sx={{ mb: 3 }}>
                      <Chip 
                        icon={isCompleted ? <CheckCircle /> : isProcessing ? <Speed /> : undefined}
                        label={isCompleted ? 'Completed' : isProcessing ? 'Processing...' : 'Pending'}
                        color={getStatusColor(isCompleted ? 'completed' : isProcessing ? 'processing' : 'pending')}
                        sx={{ 
                          fontWeight: 600,
                          borderRadius: 3,
                          height: 32,
                          px: 2,
                          background: isCompleted ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)' : 
                                       isProcessing ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%)' :
                                       'linear-gradient(135deg, rgba(156, 163, 175, 0.1) 0%, rgba(107, 114, 128, 0.05) 100%)',
                          border: isCompleted ? '1px solid rgba(34, 197, 94, 0.2)' :
                                 isProcessing ? '1px solid rgba(59, 130, 246, 0.2)' :
                                 '1px solid rgba(156, 163, 175, 0.2)'
                        }}
                      />
                    </Box>

                    {/* Processing Animation */}
                    {isProcessing && (
                      <Box sx={{ mb: 3 }}>
                        <LinearProgress 
                          sx={{ 
                            height: 6, 
                            borderRadius: 3,
                            backgroundColor: alpha(theme.palette.primary.main, 0.1),
                            '& .MuiLinearProgress-bar': {
                              borderRadius: 3,
                              background: config.gradient,
                              animation: `${shimmerAnimation} 2s infinite`
                            }
                          }} 
                        />
                      </Box>
                    )}

                    {/* Results Display */}
                    {isCompleted && result && (
                      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                        {/* Key Metrics */}
                        {result.analysis_results && (
                          <Box sx={{ mb: 3 }}>
                            {agentType === 'visual_analysis' && result.analysis_results.color_harmony_score && (
                              <Box sx={{ 
                                background: config.lightGradient,
                                borderRadius: 2,
                                p: 2,
                                mb: 1
                              }}>
                                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mb: 0.5 }}>
                                  Color Harmony
                                </Typography>
                                <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700 }}>
                                  {result.analysis_results.color_harmony_score}/10
                                </Typography>
                              </Box>
                            )}
                            {agentType === 'ux_critique' && result.analysis_results.accessibility_score && (
                              <Box sx={{ 
                                background: config.lightGradient,
                                borderRadius: 2,
                                p: 2,
                                mb: 1
                              }}>
                                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mb: 0.5 }}>
                                  Accessibility Score
                                </Typography>
                                <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700 }}>
                                  {result.analysis_results.accessibility_score}/10
                                </Typography>
                              </Box>
                            )}
                            {agentType === 'market_research' && result.analysis_results.market_positioning?.uniqueness_score && (
                              <Box sx={{ 
                                background: config.lightGradient,
                                borderRadius: 2,
                                p: 2,
                                mb: 1
                              }}>
                                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mb: 0.5 }}>
                                  Uniqueness Score
                                </Typography>
                                <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700 }}>
                                  {result.analysis_results.market_positioning.uniqueness_score}/10
                                </Typography>
                              </Box>
                            )}
                            {agentType === 'technical_feasibility' && result.analysis_results.development_complexity && (
                              <Box sx={{ 
                                background: config.lightGradient,
                                borderRadius: 2,
                                p: 2,
                                mb: 1
                              }}>
                                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mb: 0.5 }}>
                                  Development Complexity
                                </Typography>
                                <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700, textTransform: 'capitalize' }}>
                                  {result.analysis_results.development_complexity}
                                </Typography>
                              </Box>
                            )}
                            {agentType === 'brand_alignment' && result.analysis_results.brand_consistency_score && (
                              <Box sx={{ 
                                background: config.lightGradient,
                                borderRadius: 2,
                                p: 2,
                                mb: 1
                              }}>
                                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mb: 0.5 }}>
                                  Brand Consistency
                                </Typography>
                                <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700 }}>
                                  {result.analysis_results.brand_consistency_score}/10
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        )}
                        
                        {/* Recommendations */}
                        {result.recommendations && result.recommendations.length > 0 && (
                          <Box sx={{ mb: 3, flex: 1 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600, mb: 2 }}>
                              Key Recommendations:
                            </Typography>
                            <Stack spacing={1}>
                              {result.recommendations.slice(0, 3).map((rec: string, recIndex: number) => (
                                <Box key={recIndex} sx={{ 
                                  background: 'rgba(255, 255, 255, 0.5)',
                                  borderRadius: 2,
                                  p: 1.5,
                                  border: '1px solid rgba(0, 0, 0, 0.05)'
                                }}>
                                  <Typography variant="body2" sx={{ 
                                    fontStyle: 'italic', 
                                    fontSize: '0.875rem',
                                    lineHeight: 1.4
                                  }}>
                                    • {rec}
                                  </Typography>
                                </Box>
                              ))}
                              {result.recommendations.length > 3 && (
                                <Typography variant="caption" color="text.secondary" sx={{ 
                                  fontWeight: 500,
                                  textAlign: 'center',
                                  mt: 1
                                }}>
                                  +{result.recommendations.length - 3} more recommendations
                                </Typography>
                              )}
                            </Stack>
                          </Box>
                        )}
                        
                        {/* Metrics Footer */}
                        <Box sx={{ 
                          mt: 'auto',
                          pt: 2,
                          borderTop: '1px solid rgba(0, 0, 0, 0.1)',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Star sx={{ fontSize: 16, color: 'warning.main', mr: 0.5 }} />
                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                              {Math.round((result.confidence_score || 0) * 100)}% confidence
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Speed sx={{ fontSize: 16, color: 'primary.main', mr: 0.5 }} />
                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                              {result.execution_time?.toFixed(1)}s
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Fade>
            </Grid>
          )
        })}
      </Grid>

      {/* Premium Footer */}
      {status === 'completed' && (
        <Fade in timeout={1000}>
          <Box sx={{ 
            mt: 6, 
            textAlign: 'center',
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%)',
            borderRadius: 4,
            p: 4,
            border: '1px solid rgba(59, 130, 246, 0.1)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <Box sx={{ 
              position: 'absolute',
              top: -20,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 40,
              height: 40,
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, transparent 100%)',
              borderRadius: '50%'
            }} />
            <AutoAwesome sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" color="text.primary" sx={{ fontWeight: 600, mb: 1 }}>
              Analysis Completed Successfully
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Your design has been thoroughly analyzed by our AI-powered system
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
              Completed in {formatDuration(startTime, endTime)}
            </Typography>
          </Box>
        </Fade>
      )}
    </Box>
  )
}

export default AnalysisDashboard