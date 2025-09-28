'use client'

import { useState, useCallback } from 'react'
import { Container, Box, Typography, Alert, Fade, keyframes, alpha, useTheme } from '@mui/material'
import ImageUpload from './ImageUpload'
import AnalysisDashboard from './AnalysisDashboard'
import { apiService } from '@src/api'
import { UploadState, AnalysisState, AnalysisRequest } from '@/types/analysis'

function AnalysisPage() {
  const [uploadState, setUploadState] = useState<UploadState>({
    isDragActive: false,
    isDragReject: false,
    isDragAccept: false,
    selectedFile: null,
    uploadProgress: 0,
  })

  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    status: 'pending',
    progress: 0,
  })

  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unhealthy' | 'unknown'>('unknown')

  const handleFileSelect = useCallback(async (file: File) => {
    setUploadState(prev => ({ 
      ...prev, 
      selectedFile: file, 
      uploadProgress: 0,
      error: undefined 
    }))
  }, [])

  const handleStartAnalysis = useCallback(async () => {
    if (!uploadState.selectedFile) return

    try {
      setAnalysisState({
        status: 'processing',
        progress: 0,
        startTime: new Date(),
      })

      const request: AnalysisRequest = {
        image: uploadState.selectedFile,
        user_preferences: {
          industry: 'technology',
          target_audience: ['designers', 'developers'],
        },
      }

      // Start streaming the analysis directly
      await apiService.streamAnalysis(request, (event) => {
        console.log('Received event:', event)
        
        switch (event.event_type) {
          case 'progress':
            setAnalysisState(prev => ({
              ...prev,
              progress: event.data.progress || prev.progress,
            }))
            break
          case 'result':
            setAnalysisState(prev => ({
              ...prev,
              results: {
                ...prev.results,
                [event.data.agent]: event.data.result,
              },
            }))
            break
          case 'complete':
            setAnalysisState(prev => ({
              ...prev,
              status: 'completed',
              progress: 100,
              endTime: new Date(),
              results: event.data.results,
            }))
            break
          case 'error':
            setAnalysisState(prev => ({
              ...prev,
              status: 'error',
              error: event.data.message,
            }))
            break
        }
      })
    } catch (error: any) {
      console.error('Analysis failed:', error)
      setAnalysisState(prev => ({
        ...prev,
        status: 'error',
        error: error.message || 'Analysis failed',
      }))
    }
  }, [uploadState.selectedFile])

  const theme = useTheme()

  // Premium animations
  const floatingAnimation = keyframes`
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  `

  const gradientShift = keyframes`
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  `

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      backgroundSize: '400% 400%',
      animation: `${gradientShift} 15s ease infinite`,
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background decorative elements */}
      <Box sx={{
        position: 'absolute',
        top: -50,
        right: -50,
        width: 200,
        height: 200,
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%)',
        borderRadius: '50%',
        animation: `${floatingAnimation} 6s ease-in-out infinite`
      }} />
      <Box sx={{
        position: 'absolute',
        bottom: -100,
        left: -100,
        width: 300,
        height: 300,
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, transparent 100%)',
        borderRadius: '50%',
        animation: `${floatingAnimation} 8s ease-in-out infinite reverse`
      }} />
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 400,
        height: 400,
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%)',
        borderRadius: '50%',
        animation: `${floatingAnimation} 10s ease-in-out infinite`
      }} />

      <Container maxWidth="lg" sx={{ py: 6, position: 'relative', zIndex: 1 }}>
        {/* Premium Header */}
        <Fade in timeout={800}>
          <Box sx={{ 
            textAlign: 'center', 
            mb: 8,
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
            backdropFilter: 'blur(20px)',
            borderRadius: 6,
            p: 6,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 25px 50px rgba(0, 0, 0, 0.1)'
          }}>
            <Typography 
              variant="h2" 
              component="h1" 
              sx={{ 
                fontWeight: 800,
                color: 'white',
                mb: 3,
                textShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
                background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}
            >
              AI Design Analysis Suite
            </Typography>
            <Typography 
              variant="h5" 
              sx={{ 
                color: 'rgba(255, 255, 255, 0.9)',
                maxWidth: '700px',
                mx: 'auto',
                fontWeight: 400,
                lineHeight: 1.6,
                textShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
              }}
            >
              Advanced AI-powered design analysis with specialized agents for comprehensive insights and actionable recommendations
            </Typography>
          </Box>
        </Fade>

        {/* Health Status Alert */}
        {healthStatus === 'unhealthy' && (
          <Fade in timeout={500}>
            <Alert 
              severity="warning" 
              sx={{ 
                mb: 4,
                borderRadius: 4,
                background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%)',
                border: '1px solid rgba(245, 158, 11, 0.2)',
                backdropFilter: 'blur(10px)',
                color: 'white'
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, color: 'inherit' }}>
                Service Unavailable
              </Typography>
              <Typography variant="body2" sx={{ color: 'inherit' }}>
                Backend service is currently unavailable. Please check your connection.
              </Typography>
            </Alert>
          </Fade>
        )}

        {/* Main Content */}
        <Fade in timeout={1000}>
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: 6,
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%)',
            backdropFilter: 'blur(20px)',
            borderRadius: 6,
            p: 6,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 25px 50px rgba(0, 0, 0, 0.1)'
          }}>
            <ImageUpload
              onFileSelect={handleFileSelect}
              uploadState={uploadState}
              disabled={analysisState.status === 'processing'}
              onStartAnalysis={handleStartAnalysis}
            />

            <AnalysisDashboard analysisState={analysisState} />
          </Box>
        </Fade>
      </Container>
    </Box>
  )
}

export default AnalysisPage
