// src/pages/OAuthCallbackPage.tsx
import { useEffect, useRef } from 'react'
import { useOAuth } from '../hooks/useOAuth'
import { LoadingOverlay } from '../components/LoadingOverlay/LoadingOverlay'

export default function OAuthCallbackPage() {
  const { handleCallback } = useOAuth()
  const ran = useRef(false)
  useEffect(() => {
    if (ran.current) return
    ran.current = true
    void handleCallback()
  }, [handleCallback])
  return <LoadingOverlay message="Обработка..." />
}
