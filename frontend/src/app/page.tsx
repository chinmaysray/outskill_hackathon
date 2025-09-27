import { Suspense } from 'react'
import { Box } from '@mui/material'
import AnalysisPage from '@/components/AnalysisPage'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import ErrorBoundary from '@/components/ui/ErrorBoundary'

export default function HomePage() {
  return (
    <Box
      component="main"
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%)',
      }}
    >
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <AnalysisPage />
        </Suspense>
      </ErrorBoundary>
    </Box>
  )
}
