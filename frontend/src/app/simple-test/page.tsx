'use client'

import { useState } from 'react'
import { Button, Box, Typography, Paper } from '@mui/material'

export default function SimpleUploadTest() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleStartAnalysis = () => {
    if (selectedFile) {
      alert(`Starting analysis for: ${selectedFile.name}`)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <Typography variant="h4" gutterBottom>
        Simple Upload Test
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          File Upload Test
        </Typography>
        
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ marginBottom: '20px' }}
        />
        
        {selectedFile && (
          <Box>
            <Typography variant="body1" color="success.main" gutterBottom>
              Selected: {selectedFile.name}
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleStartAnalysis}
              sx={{ mt: 2 }}
            >
              Start Analysis
            </Button>
          </Box>
        )}
      </Paper>
    </div>
  )
}
