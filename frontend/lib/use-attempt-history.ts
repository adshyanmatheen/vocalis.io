'use client'

import { useCallback, useState } from 'react'

export type AttemptSnapshot = {
  score: number
  createdAt: string
  weakCount: number
  durationSeconds: number
}

const ATTEMPT_HISTORY_STORAGE_KEY = 'vocalis-attempt-history'
const MAX_ATTEMPT_HISTORY_ITEMS = 8

const readAttemptHistory = () => {
  if (typeof window === 'undefined') {
    return []
  }

  const savedHistory = window.localStorage.getItem(ATTEMPT_HISTORY_STORAGE_KEY)
  if (!savedHistory) {
    return []
  }

  try {
    const parsed = JSON.parse(savedHistory) as AttemptSnapshot[]
    return Array.isArray(parsed) ? parsed.slice(-MAX_ATTEMPT_HISTORY_ITEMS) : []
  } catch {
    return []
  }
}

export const useAttemptHistory = () => {
  const [attemptHistory, setAttemptHistory] = useState<AttemptSnapshot[]>(readAttemptHistory)

  const appendAttempt = useCallback((snapshot: AttemptSnapshot) => {
    setAttemptHistory((previous) => {
      const next = [...previous, snapshot].slice(-MAX_ATTEMPT_HISTORY_ITEMS)
      localStorage.setItem(ATTEMPT_HISTORY_STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }, [])

  return {
    attemptHistory,
    appendAttempt,
  }
}
