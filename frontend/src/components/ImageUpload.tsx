'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { 
  Box, 
  Typography, 
  Paper, 
  LinearProgress, 
  Alert,
  Button,
  Stack,
  Fade,
  Zoom,
  useTheme,
  alpha,
  keyframes
} from '@mui/material'
import { 
  CloudUpload, 
  Image as ImageIcon, 
  CheckCircle,
  PlayArrow,
  AutoAwesome,
  Upload,
  PhotoCamera
} from '@mui/icons-material'
import { UploadState } from '@/types/analysis'

interface ImageUploadProps {
  onFileSelect: (file: File) => void
  uploadState: UploadState
  disabled?: boolean
  onStartAnalysis?: () => void
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

const floatAnimation = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
`

const gradientShift = keyframes`
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
`

function ImageUpload({ 
  onFileSelect, 
  uploadState, 
  disabled = false,
  onStartAnalysis 
}: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const theme = useTheme()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      onFileSelect(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled,
  })

  const getDropzoneStyles = () => {
    if (isDragReject) {
      return {
        borderColor: '#ef4444',
        backgroundColor: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%)',
        boxShadow: '0 0 30px rgba(239, 68, 68, 0.3)',
        transform: 'scale(0.98)',
      }
    }
    if (isDragActive) {
      return {
        borderColor: '#667eea',
        backgroundColor: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%)',
        boxShadow: '0 0 40px rgba(102, 126, 234, 0.4)',
        transform: 'scale(1.02)',
      }
    }
    return {
      borderColor: 'rgba(255, 255, 255, 0.3)',
      backgroundColor: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(248, 250, 252, 0.1) 100%)',
    }
  }

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Error Alert */}
      {uploadState.error && (
        <Fade in timeout={300}>
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3,
              borderRadius: 4,
              background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 10px 30px rgba(239, 68, 68, 0.1)'
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              Upload Error
            </Typography>
            <Typography variant="body2">
              {uploadState.error}
            </Typography>
          </Alert>
        </Fade>
      )}

      {/* Main Upload Area */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          borderRadius: 6,
          border: '2px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
            opacity: 0.8
          }
        }}
      >
        <Box sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{ 
              display: 'inline-flex',
              alignItems: 'center',
              gap: 2,
              mb: 2
            }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: 3, 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)'
              }}>
                <PhotoCamera sx={{ fontSize: 28 }} />
              </Box>
              <Typography variant="h5" color="text.primary" sx={{ fontWeight: 700 }}>
                Upload Design Image
              </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500, mx: 'auto' }}>
              Upload your design image to get comprehensive AI-powered analysis and insights
            </Typography>
          </Box>

          {/* Dropzone */}
          <Box
            {...getRootProps()}
            sx={{
              border: 2,
              borderStyle: 'dashed',
              borderRadius: 4,
              p: 6,
              textAlign: 'center',
              cursor: disabled ? 'not-allowed' : 'pointer',
              opacity: disabled ? 0.6 : 1,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
              overflow: 'hidden',
              ...getDropzoneStyles(),
              '&:hover': !disabled ? {
                transform: 'translateY(-2px)',
                boxShadow: '0 15px 35px rgba(0, 0, 0, 0.1)',
              } : {},
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
                opacity: isDragActive ? 1 : 0,
                transition: 'opacity 0.3s ease'
              }
            }}
          >
            <input {...getInputProps()} />
            
            <Stack spacing={3} alignItems="center" sx={{ position: 'relative', zIndex: 1 }}>
              {preview ? (
                <Zoom in timeout={500}>
                  <Box sx={{ position: 'relative' }}>
                    <img
                      src={preview}
                      alt="Preview"
                      style={{
                        maxWidth: '250px',
                        maxHeight: '250px',
                        borderRadius: '12px',
                        objectFit: 'cover',
                        boxShadow: '0 15px 35px rgba(0, 0, 0, 0.2)',
                        border: '3px solid white'
                      }}
                    />
                    <Box sx={{
                      position: 'absolute',
                      top: -8,
                      right: -8,
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      borderRadius: '50%',
                      p: 1,
                      boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                      animation: `${pulseAnimation} 2s infinite`
                    }}>
                      <CheckCircle sx={{ color: 'white', fontSize: 24 }} />
                    </Box>
                  </Box>
                </Zoom>
              ) : (
                <Box sx={{ 
                  position: 'relative',
                  animation: `${floatAnimation} 3s ease-in-out infinite`
                }}>
                  <Box sx={{ 
                    p: 3, 
                    borderRadius: 4, 
                    background: isDragActive 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
                    color: isDragActive ? 'white' : 'primary.main',
                    transition: 'all 0.3s ease',
                    boxShadow: isDragActive ? '0 15px 35px rgba(102, 126, 234, 0.4)' : '0 8px 25px rgba(102, 126, 234, 0.2)'
                  }}>
                    {isDragActive ? (
                      <CloudUpload sx={{ fontSize: 64 }} />
                    ) : (
                      <Upload sx={{ fontSize: 64 }} />
                    )}
                  </Box>
                </Box>
              )}

              <Box>
                <Typography 
                  variant="h6" 
                  color="text.primary" 
                  sx={{ 
                    fontWeight: 600, 
                    mb: 1,
                    color: isDragActive ? '#667eea' : 'inherit'
                  }}
                >
                  {isDragActive
                    ? 'Drop your image here!'
                    : preview
                    ? 'Image ready for analysis'
                    : 'Drag & drop your design image here'
                  }
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {isDragActive
                    ? 'Release to upload'
                    : preview
                    ? 'Click to change image'
                    : 'or click to browse files'
                  }
                </Typography>
                <Box sx={{ 
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 1,
                  px: 2,
                  py: 1,
                  background: 'rgba(102, 126, 234, 0.1)',
                  borderRadius: 3,
                  border: '1px solid rgba(102, 126, 234, 0.2)'
                }}>
                  <ImageIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                  <Typography variant="caption" color="primary.main" sx={{ fontWeight: 500 }}>
                    JPG, PNG, GIF, BMP, WebP (max 10MB)
                  </Typography>
                </Box>
              </Box>

              {/* Upload Progress */}
              {uploadState.uploadProgress > 0 && (
                <Fade in timeout={300}>
                  <Box sx={{ width: '100%', maxWidth: 300 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={uploadState.uploadProgress}
                      sx={{ 
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                          background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                          animation: `${shimmerAnimation} 2s infinite`
                        }
                      }}
                    />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, fontWeight: 500 }}>
                      Uploading... {uploadState.uploadProgress}%
                    </Typography>
                  </Box>
                </Fade>
              )}
            </Stack>
          </Box>
        </Box>
      </Box>

      {/* Start Analysis Button */}
      {uploadState.selectedFile && !disabled && (
        <Fade in timeout={600}>
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<AutoAwesome />}
              onClick={onStartAnalysis}
              disabled={disabled}
              sx={{
                px: 6,
                py: 2,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 15px 35px rgba(102, 126, 234, 0.4)',
                fontWeight: 600,
                fontSize: '1.1rem',
                textTransform: 'none',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 20px 40px rgba(102, 126, 234, 0.6)',
                  background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                },
                '&:active': {
                  transform: 'translateY(0px)',
                }
              }}
            >
              Start AI Analysis
            </Button>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2, fontWeight: 500 }}>
              Comprehensive analysis by 5 specialized AI agents
            </Typography>
          </Box>
        </Fade>
      )}
    </Box>
  )
}

export default ImageUpload