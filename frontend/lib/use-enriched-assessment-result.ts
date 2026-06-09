'use client'

import { useMemo } from 'react'

import {
  buildAssessmentSummary,
  getWordScoreLabel,
  getWordScoreValue,
  isGenericAssessmentSummary,
} from '@/lib/home-assessment'
import type { AssessmentCompletedEvent, FeedbackWordDiagnostic } from '@/lib/realtime-assessment'
import type { AttemptSnapshot } from '@/lib/use-attempt-history'

export const useEnrichedAssessmentResult = (
  assessmentResult: AssessmentCompletedEvent | null,
  attemptHistory: AttemptSnapshot[],
) =>
  useMemo(() => {
    if (!assessmentResult) {
      return null
    }

    const previousAttempt =
      attemptHistory.length > 0 ? attemptHistory[attemptHistory.length - 1] : null
    const sortedWordScores = [...assessmentResult.word_scores]
      .map((wordScore) => ({
        word: getWordScoreLabel(wordScore),
        score: getWordScoreValue(wordScore),
        phoneme_count: typeof wordScore.phoneme_count === 'number' ? wordScore.phoneme_count : 0,
      }))
      .sort((a, b) => a.score - b.score)

    const weakestWords: FeedbackWordDiagnostic[] = sortedWordScores.slice(0, 3).map((item) => ({
      word: item.word,
      score: item.score,
      phoneme_count: item.phoneme_count,
    }))
    const strongestWords: FeedbackWordDiagnostic[] = [...sortedWordScores]
      .reverse()
      .slice(0, 3)
      .map((item) => ({
        word: item.word,
        score: item.score,
        phoneme_count: item.phoneme_count,
      }))

    const averageWordConfidence = sortedWordScores.length
      ? sortedWordScores.reduce((sum, item) => sum + item.score, 0) / sortedWordScores.length
      : 0
    const durationSeconds =
      typeof assessmentResult.feedback.realtime?.duration_seconds === 'number'
        ? assessmentResult.feedback.realtime.duration_seconds
        : 0
    const speechPaceWpm = durationSeconds > 0 ? (sortedWordScores.length / durationSeconds) * 60 : 0
    const trendDelta = previousAttempt
      ? assessmentResult.overall_score - previousAttempt.score
      : null

    const generatedSummary = buildAssessmentSummary({
      score: assessmentResult.overall_score,
      performanceBand: assessmentResult.performance_band,
      weakPhonemes: assessmentResult.weak_phonemes,
      weakestWords,
      trendDelta,
    })

    return {
      summary: isGenericAssessmentSummary(assessmentResult.feedback.summary)
        ? generatedSummary
        : assessmentResult.feedback.summary,
      metrics: {
        accuracy_percent:
          typeof assessmentResult.feedback.metrics?.accuracy_percent === 'number'
            ? assessmentResult.feedback.metrics.accuracy_percent
            : Math.round(Math.max(0, Math.min(1, assessmentResult.overall_score)) * 1000) / 10,
        speech_pace_wpm:
          typeof assessmentResult.feedback.metrics?.speech_pace_wpm === 'number'
            ? assessmentResult.feedback.metrics.speech_pace_wpm
            : speechPaceWpm,
        average_word_confidence:
          typeof assessmentResult.feedback.metrics?.average_word_confidence === 'number'
            ? assessmentResult.feedback.metrics.average_word_confidence
            : averageWordConfidence,
        duration_seconds:
          typeof assessmentResult.feedback.realtime?.duration_seconds === 'number'
            ? assessmentResult.feedback.realtime.duration_seconds
            : undefined,
      },
      actionChecklist: assessmentResult.feedback.action_items?.length
        ? assessmentResult.feedback.action_items.slice(0, 3)
        : [
            'Complete one focused 2-minute pronunciation drill.',
            'Re-record at a slightly slower pace for cleaner consonants.',
            'Aim to improve the overall score by 5% in the next attempt.',
          ],
      wordDiagnostics: {
        weakest_words: assessmentResult.feedback.word_diagnostics?.weakest_words?.length
          ? assessmentResult.feedback.word_diagnostics.weakest_words
          : weakestWords,
        strongest_words: assessmentResult.feedback.word_diagnostics?.strongest_words?.length
          ? assessmentResult.feedback.word_diagnostics.strongest_words
          : strongestWords,
      },
    }
  }, [assessmentResult, attemptHistory])
