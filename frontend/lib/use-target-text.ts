'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import { getApiBaseUrl } from '@/lib/api'
import { fallbackTargetText, type TargetText } from '@/lib/home-assessment'

export const useTargetText = () => {
  const [targetText, setTargetText] = useState(fallbackTargetText)
  const requestIdRef = useRef(0)
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort()
    }
  }, [])

  const loadTargetText = useCallback(async (focusPhonemes?: string[]) => {
    abortControllerRef.current?.abort()

    const requestId = ++requestIdRef.current
    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      const baseUrl = new URL(`${getApiBaseUrl()}/targets/current`)
      const normalizedFocus = (focusPhonemes ?? []).map((value) => value.trim()).filter(Boolean)

      if (normalizedFocus.length > 0) {
        baseUrl.searchParams.set('focus_phonemes', normalizedFocus.join(','))
      }

      const response = await fetch(baseUrl.toString(), {
        method: 'GET',
        signal: controller.signal,
      })

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload?.detail || payload?.message || 'Unable to load target text.')
      }

      if (requestId === requestIdRef.current) {
        setTargetText((payload as TargetText).text)
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        return
      }
      if (requestId === requestIdRef.current) {
        setTargetText(fallbackTargetText)
      }
    }
  }, [])

  return {
    targetText,
    loadTargetText,
  }
}
