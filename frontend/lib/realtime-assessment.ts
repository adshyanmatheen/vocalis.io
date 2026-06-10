import { getApiBaseUrl } from '@/lib/api'
import type { ModelHealthResponse as GeneratedModelHealthResponse } from '@/lib/generated/api-types'
import {
  REALTIME_SAMPLE_RATE,
  audioBufferToPcm16Bytes,
  chunkPcm16Bytes,
  pcm16BytesToBase64,
  resampleAudioBuffer,
} from '@/lib/audio/pcm16'

export type WordScore = {
  word?: string
  text?: string
  score?: number
  weighted_score?: number
  confidence?: number
  average_confidence?: number
  phoneme_count?: number
  performance_band?: string
  [key: string]: unknown
}

export type FeedbackWordDiagnostic = {
  word: string
  score: number
  phoneme_count: number
}

export type RealtimeFeedback = {
  summary?: string
  action_items?: string[]
  encouragement?: string
  metrics?: {
    overall_score?: number
    accuracy_percent?: number
    performance_band?: string
    weak_phoneme_count?: number
    practiced_word_count?: number
    average_word_confidence?: number
    speech_pace_wpm?: number
    [key: string]: unknown
  }
  highlights?: {
    top_weak_phonemes?: string[]
    next_focus?: string[]
    has_weak_phonemes?: boolean
    [key: string]: unknown
  }
  word_diagnostics?: {
    weakest_words?: FeedbackWordDiagnostic[]
    strongest_words?: FeedbackWordDiagnostic[]
    [key: string]: unknown
  }
  error_breakdown?: {
    total_scored_phonemes?: number
    error_types?: Record<string, number>
    severity_distribution?: Record<string, number>
    [key: string]: unknown
  }
  coaching_plan?: string[]
  realtime?: {
    duration_seconds?: number
    source?: string
    [key: string]: unknown
  }
  [key: string]: unknown
}

export type AssessmentCompletedEvent = {
  type: 'assessment_completed'
  overall_score: number
  performance_band: string
  feedback: RealtimeFeedback
  weak_phonemes: string[]
  word_scores: WordScore[]
}

export type PartialFeedbackEvent = {
  type: 'partial_feedback'
  overall_score: number
  performance_band: string
  weak_phonemes: string[]
  word_scores: WordScore[]
}

type AssessmentStartedEvent = {
  type: 'assessment_started'
  target_text: string
  sample_rate: number
}

type AssessmentErrorEvent = {
  type: 'assessment_error'
  message: string
}

type AssessmentEvent =
  | AssessmentStartedEvent
  | PartialFeedbackEvent
  | AssessmentCompletedEvent
  | AssessmentErrorEvent

type SubmitRealtimeAssessmentOptions = {
  targetText: string
  audioBuffer: AudioBuffer
  onPartialFeedback?: (event: PartialFeedbackEvent) => void
}

export type ModelHealthResponse = Omit<GeneratedModelHealthResponse, 'models'> & {
  ready: boolean
  status: string
  cache_dir: string
  device: string
  started_at: string
  preload_task_status: string
  realtime_inference_timeout_seconds: number
  models: Array<{
    name: string
    model_id: string
    status: string
    error: string | null
    updated_at: string | null
    load_started_at?: string | null
    load_finished_at?: string | null
    load_duration_seconds?: number | null
  }>
}

const getAssessmentWebSocketUrl = () => {
  const apiUrl = new URL(getApiBaseUrl())
  apiUrl.protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
  apiUrl.pathname = '/ws/assessment'
  apiUrl.search = ''
  apiUrl.hash = ''

  return apiUrl.toString()
}

const sanitizeTargetTextForAlignment = (text: string) => {
  return text
    .replace(/[.?!,;:]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

const parseAssessmentEvent = (data: unknown): AssessmentEvent => {
  if (typeof data !== 'string') {
    throw new Error('The Assessment Server Returned an invalid event.')
  }

  const event = JSON.parse(data) as AssessmentEvent

  if (!event || typeof event.type !== 'string') {
    throw new Error('The assessment server returned an invalid event.')
  }

  return event
}

export const getModelHealth = async (signal?: AbortSignal) => {
  const response = await fetch(`${getApiBaseUrl()}/health/models`, {
    method: 'GET',
    signal,
  })
  const payload = await response.json()

  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || 'Unable to check model readiness.')
  }

  if (typeof payload !== 'object' || payload === null) {
    throw new Error('Invalid model health response.')
  }

  return payload as ModelHealthResponse
}

export const getModelHealthMessage = (modelHealth: ModelHealthResponse) => {
  const loadingModels = modelHealth.models.filter((model) => model.status === 'loading')
  const failedModels = modelHealth.models.filter((model) => model.status === 'failed')

  if (modelHealth.ready) {
    return null
  }

  if (loadingModels.length > 0) {
    return 'Preparing Assessment Engine. Please try again in a moment.'
  }

  if (failedModels.length > 0) {
    return 'Assessment engine setup is incomplete. Please contact support or try again later.'
  }

  return 'Assessment engine is not ready yet. Please try again later.'
}

export const submitRealtimeAssessment = async ({
  targetText,
  audioBuffer,
  onPartialFeedback,
}: SubmitRealtimeAssessmentOptions) => {
  const realtimeAudioBuffer = await resampleAudioBuffer(audioBuffer, REALTIME_SAMPLE_RATE)

  return new Promise<AssessmentCompletedEvent>((resolve, reject) => {
    const socket = new WebSocket(getAssessmentWebSocketUrl())
    const sampleRate = REALTIME_SAMPLE_RATE
    const sanitizedTargetText = sanitizeTargetTextForAlignment(targetText)
    const chunks = chunkPcm16Bytes(audioBufferToPcm16Bytes(realtimeAudioBuffer), sampleRate)
    let settled = false

    const ASSESSMENT_TIMEOUT_MS = 30_000

    const settle = (callback: () => void) => {
      if (settled) {
        return
      }

      settled = true
      clearTimeout(timeoutId)
      callback()
      socket.close()
    }

    const timeoutId = setTimeout(() => {
      settle(() => reject(new Error('Assessment timed out. Please try again.')))
    }, ASSESSMENT_TIMEOUT_MS)

    socket.addEventListener('open', () => {
      try {
        socket.send(
          JSON.stringify({
            type: 'start_assessment',
            target_text: sanitizedTargetText,
            sample_rate: sampleRate,
          }),
        )

        for (const [index, chunk] of chunks.entries()) {
          socket.send(
            JSON.stringify({
              type: 'audio_chunk',
              audio: pcm16BytesToBase64(chunk),
              sequence: index + 1,
              sample_rate: sampleRate,
            }),
          )
        }

        socket.send(JSON.stringify({ type: 'end_assessment' }))
      } catch (error) {
        settle(() =>
          reject(
            error instanceof Error
              ? error
              : new Error('Failed to send audio data to the assessment server.'),
          ),
        )
      }
    })

    socket.addEventListener('message', (message) => {
      try {
        const event = parseAssessmentEvent(message.data)

        if (event.type === 'partial_feedback') {
          onPartialFeedback?.(event)
          return
        }

        if (event.type === 'assessment_completed') {
          settle(() => resolve(event))
          return
        }

        if (event.type === 'assessment_error') {
          const rawMessage = typeof event.message === 'string' ? event.message : ''
          const mappedMessage = rawMessage.includes('Unsupported Alignment Character Detected')
            ? 'Assessment text contains unsupported punctuation. Try removing punctuation (like periods) and try again.'
            : rawMessage || 'The assessment server reported an error.'

          settle(() => reject(new Error(mappedMessage)))
        }
      } catch (error) {
        settle(() =>
          reject(
            error instanceof Error ? error : new Error('Unable to read the assessment response.'),
          ),
        )
      }
    })

    socket.addEventListener('error', () => {
      settle(() => reject(new Error('Unable to connect to the assessment server.')))
    })

    socket.addEventListener('close', () => {
      if (!settled) {
        settle(() => reject(new Error('The assessment connection closed early.')))
      }
    })
  })
}
