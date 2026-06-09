import { describe, expect, it } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useEnrichedAssessmentResult } from '@/lib/use-enriched-assessment-result'
import type { AssessmentCompletedEvent } from '@/lib/realtime-assessment'
import type { AttemptSnapshot } from '@/lib/use-attempt-history'

const mockAssessmentResult: AssessmentCompletedEvent = {
  type: 'assessment_completed',
  overall_score: 0.78,
  performance_band: 'Strong',
  weak_phonemes: ['r'],
  word_scores: [
    {
      word: 'rabbit',
      score: 0.95,
      phoneme_count: 5,
      weighted_score: 0.93,
      average_confidence: 0.94,
    },
    { word: 'run', score: 0.45, phoneme_count: 3, weighted_score: 0.42, average_confidence: 0.44 },
    { word: 'fast', score: 0.85, phoneme_count: 4, weighted_score: 0.87, average_confidence: 0.86 },
  ],
  feedback: {
    summary: 'Realtime pronunciation assessment completed.',
    metrics: {
      accuracy_percent: 78,
    },
    realtime: {
      duration_seconds: 3.5,
    },
    action_items: [],
    word_diagnostics: {
      weakest_words: [],
      strongest_words: [],
    },
  },
}

describe('useEnrichedAssessmentResult', () => {
  it('returns null when assessmentResult is null', () => {
    const { result } = renderHook(() => useEnrichedAssessmentResult(null, []))
    expect(result.current).toBeNull()
  })

  it('computes weakest and strongest words', () => {
    const { result } = renderHook(() => useEnrichedAssessmentResult(mockAssessmentResult, []))
    expect(result.current).not.toBeNull()
    expect(result.current!.wordDiagnostics.weakest_words).toHaveLength(3)
    expect(result.current!.wordDiagnostics.weakest_words[0].word).toBe('run')
    expect(result.current!.wordDiagnostics.strongest_words[0].word).toBe('rabbit')
  })

  it('computes averageWordConfidence', () => {
    const { result } = renderHook(() => useEnrichedAssessmentResult(mockAssessmentResult, []))
    const avg = (0.93 + 0.42 + 0.87) / 3
    expect(result.current!.metrics.average_word_confidence).toBeCloseTo(avg, 5)
  })

  it('computes speech pace WPM', () => {
    const { result } = renderHook(() => useEnrichedAssessmentResult(mockAssessmentResult, []))
    const wpm = (3 / 3.5) * 60
    expect(result.current!.metrics.speech_pace_wpm).toBeCloseTo(wpm, 5)
  })

  it('computes trend delta with previous attempt', () => {
    const history: AttemptSnapshot[] = [
      { score: 0.7, createdAt: '2024-01-01T00:00:00Z', weakCount: 4, durationSeconds: 40 },
    ]
    const { result } = renderHook(() => useEnrichedAssessmentResult(mockAssessmentResult, history))
    expect(result.current!.summary).toContain('Up 8')
  })

  it('uses custom summary when not generic', () => {
    const customResult: AssessmentCompletedEvent = {
      ...mockAssessmentResult,
      feedback: {
        ...mockAssessmentResult.feedback,
        summary: 'Great progress on /r/!',
      },
    }
    const { result } = renderHook(() => useEnrichedAssessmentResult(customResult, []))
    expect(result.current!.summary).toBe('Great progress on /r/!')
  })

  it('falls back to generated summary for generic summary', () => {
    const { result } = renderHook(() => useEnrichedAssessmentResult(mockAssessmentResult, []))
    expect(result.current!.summary).not.toBe('Realtime pronunciation assessment completed.')
    expect(result.current!.summary).toContain('78%')
  })
})
