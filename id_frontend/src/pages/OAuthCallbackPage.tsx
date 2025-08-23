// src/pages/OAuthCallbackPage.tsx
import { useEffect } from 'react'
import { useOAuth } from '../hooks/useOAuth'
import { LoadingOverlay } from '../components/LoadingOverlay/LoadingOverlay'

export default function OAuthCallbackPage() {
  const { handleCallback } = useOAuth()
  useEffect(() => { void handleCallback() }, [handleCallback])
  return <LoadingOverlay message="Обработка..." />
}
