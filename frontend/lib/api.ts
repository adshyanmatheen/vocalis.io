import type { AccountSummaryResponse, AuthUserResponse } from '@/lib/generated/api-types'

export const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL
  }

  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:8000/api/v1`
  }

  return 'http://localhost:8000/api/v1'
}

export type AuthUser = AuthUserResponse

export type AccountRecentAttempt = {
  id: number
  target_text: string
  target_difficulty: string
  overall_score: number
  performance_band: string
  weak_phonemes: string[]
  created_at: string
}

export type AccountSummary = AccountSummaryResponse & {
  user: AuthUser & {
    created_at: string
    mfa_enabled: boolean
    is_active: boolean
  }
  activity: {
    total_attempts: number
    average_score: number
    best_score: number
    latest_score: number
    latest_attempt_at: string | null
    recent_attempts: AccountRecentAttempt[]
  }
  progress: {
    score_series: Array<{
      attempt_id: number
      score: number
      created_at: string
    }>
    performance_band_counts: Record<string, number>
    recent_weak_phonemes: Array<{
      phoneme: string
      count: number
    }>
  }
  personalization: {
    current_focus: string | null
    recurring_sound_note: string | null
    improvement_note: string | null
    consistency_note: string | null
    focus_phonemes: Array<{
      phoneme: string
      total_occurrences: number
      weak_occurrences: number
      average_score: number
      average_severity_score: number
      recent_weighted_score: number
      common_error_types: string[]
      trend_direction: string
      consistency_score: number
      trend_confidence: number
      last_seen_at: string
    }>
  }
}

const CSRF_COOKIE_NAME = 'csrf_token'

export function csrfHeader(): Record<string, string> {
  if (typeof document === 'undefined') return {}
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${CSRF_COOKIE_NAME}=([^;]*)`))
  const token = match?.[1] ?? ''
  return token ? { 'X-CSRF-Token': token } : {}
}

const withCredentials = {
  credentials: 'include' as const,
}

export const fetchCurrentUser = async (signal?: AbortSignal): Promise<AuthUser | null> => {
  const response = await fetch(`${getApiBaseUrl()}/auth/me`, {
    method: 'GET',
    ...withCredentials,
    signal,
  })
  if (!response.ok) {
    return null
  }
  return response.json() as Promise<AuthUser>
}

export const refreshUserSession = async (signal?: AbortSignal): Promise<boolean> => {
  const response = await fetch(`${getApiBaseUrl()}/auth/refresh`, {
    method: 'POST',
    ...withCredentials,
    headers: { ...csrfHeader() },
    signal,
  })
  return response.ok
}

export const getSessionUserWithRefresh = async (signal?: AbortSignal): Promise<AuthUser | null> => {
  const currentUser = await fetchCurrentUser(signal)
  if (currentUser) {
    return currentUser
  }
  const refreshed = await refreshUserSession(signal)
  if (!refreshed) {
    return null
  }
  return fetchCurrentUser(signal)
}

export const fetchAccountSummary = async (signal?: AbortSignal): Promise<AccountSummary> => {
  const response = await fetch(`${getApiBaseUrl()}/account/summary`, {
    method: 'GET',
    ...withCredentials,
    signal,
  })
  const payload = await response.json()

  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || 'Unable to load account summary.')
  }

  return payload as AccountSummary
}

export const logoutUser = async (signal?: AbortSignal): Promise<boolean> => {
  const response = await fetch(`${getApiBaseUrl()}/auth/logout`, {
    method: 'POST',
    ...withCredentials,
    headers: { ...csrfHeader() },
    signal,
  })

  return response.ok
}
