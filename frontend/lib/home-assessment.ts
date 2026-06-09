import type { WordScore } from '@/lib/realtime-assessment'

export type TargetText = {
  id: string
  text: string
  difficulty: string
  category: string
  articulation_focus: string[]
  word_count: number
}

export type VoiceState =
  | 'idle'
  | 'preparing'
  | 'recording'
  | 'preprocessing'
  | 'submitting'
  | 'completed'
  | 'error'

export const fallbackTargetText = 'The quick brown fox jumps over the lazy dog.'

export const dotMeters = Array.from({ length: 8 })

export const getTimeBasedGreeting = () => {
  const hour = new Date().getHours()

  if (hour < 12) {
    return 'Good Morning'
  }

  if (hour < 17) {
    return 'Good Afternoon'
  }

  if (hour < 21) {
    return 'Good Evening'
  }

  return 'Good Night'
}

export const getUserInitials = (name: string | undefined) => {
  if (!name?.trim()) {
    return 'V'
  }

  const initials = name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

  return initials || 'V'
}

export const getOverallScorePercent = (score: number | undefined) => {
  if (typeof score !== 'number' || Number.isNaN(score)) {
    return 0
  }

  const normalizedScore = score > 1 ? score / 100 : score
  return Math.round(Math.max(0, Math.min(1, normalizedScore)) * 100)
}

export const formatScore = (score: number | undefined) => `${getOverallScorePercent(score)}%`

export const getWordScoreValue = (wordScore: WordScore) => {
  const rawCandidates: unknown[] = [
    wordScore.weighted_score,
    wordScore.score,
    wordScore.average_confidence,
    wordScore.confidence,
    wordScore['overall_score'],
    wordScore['pronunciation_score'],
    wordScore['accuracy'],
  ]

  for (const candidate of rawCandidates) {
    if (typeof candidate === 'number' && !Number.isNaN(candidate)) {
      return candidate
    }

    if (typeof candidate === 'string') {
      const parsed = Number.parseFloat(candidate)
      if (!Number.isNaN(parsed)) {
        return parsed
      }
    }
  }

  return 0
}

export const getWordScoreLabel = (wordScore: WordScore) =>
  wordScore.word || wordScore.text || 'Word'

export const formatMetricNumber = (value: unknown, digits = 1) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '--'
  }

  return value.toFixed(digits)
}

export const isGenericAssessmentSummary = (summary: string | undefined) => {
  if (!summary) {
    return true
  }

  return (
    summary === 'Realtime pronunciation assessment completed.' ||
    summary.startsWith('Realtime assessment complete:')
  )
}

export const buildAssessmentSummary = (params: {
  score: number
  performanceBand: string
  weakPhonemes: string[]
  weakestWords: { word: string }[]
  trendDelta: number | null
}) => {
  const scorePct = getOverallScorePercent(params.score)
  const focusSounds = params.weakPhonemes
    .slice(0, 3)
    .map((phoneme) => `/${phoneme}/`)
    .join(', ')
  const weakWordNames = params.weakestWords
    .map((item) => item.word.trim())
    .filter(Boolean)
    .slice(0, 3)

  const trendNote =
    params.trendDelta === null
      ? ''
      : params.trendDelta > 0.02
        ? ` Up ${Math.round(params.trendDelta * 100)} points from your last take.`
        : params.trendDelta < -0.02
          ? ` Down ${Math.round(Math.abs(params.trendDelta) * 100)} points from your last take-try a slower retry.`
          : ''

  let wordClause = ''
  if (weakWordNames.length === 1) {
    wordClause = ` "${weakWordNames[0]}" struggled most`
  } else if (weakWordNames.length === 2) {
    wordClause = ` "${weakWordNames[0]}" and "${weakWordNames[1]}" struggled most`
  } else if (weakWordNames.length >= 3) {
    wordClause = ` "${weakWordNames[0]}", "${weakWordNames[1]}", and "${weakWordNames[2]}" struggled most`
  }

  if (params.weakPhonemes.length === 0) {
    if (scorePct >= 80) {
      return `At ${scorePct}%, you held ${params.performanceBand.toLowerCase()} clarity with no flagged sound gaps.${trendNote} Keep this articulation and add a little speed next round.`
    }

    return `You scored ${scorePct}% (${params.performanceBand}) without a dominant weak sound-clarity may be pacing or vowel shape.${trendNote} Slow the line slightly and stress each syllable on the way out.`
  }

  const wordSuffix = wordClause ? `;${wordClause}.` : ''

  if (scorePct >= 75) {
    return `Strong ${scorePct}% run.${trendNote} Polish ${focusSounds}${wordSuffix}`
  }

  if (scorePct >= 50) {
    return `${scorePct}% puts you in ${params.performanceBand} territory.${trendNote} Lead with ${focusSounds}${wordSuffix || '; drill each sound in isolation, then read the full line at half speed.'}`
  }

  return `${scorePct}%-articulation is being pulled down by ${focusSounds}${wordSuffix || '.'}${trendNote} Work the top sound slowly, then replay the full passage once.`.trim()
}

const WEAK_PHONEME_TIERS = [
  {
    label: 'Primary',
    rowClassName: 'border-l-red-400',
    labelClassName: 'text-red-300',
    statusClassName: 'text-red-300/80',
  },
  {
    label: 'Secondary',
    rowClassName: 'border-l-amber-400',
    labelClassName: 'text-amber-300',
    statusClassName: 'text-amber-300/80',
  },
  {
    label: 'Tertiary',
    rowClassName: 'border-l-yellow-300',
    labelClassName: 'text-yellow-200',
    statusClassName: 'text-yellow-200/80',
  },
] as const

const MAX_RESIDUAL_PHONEMES_DISPLAYED = 4

export const MAX_WEAK_PHONEMES_DISPLAYED =
  WEAK_PHONEME_TIERS.length + MAX_RESIDUAL_PHONEMES_DISPLAYED

export const getWeakPhonemeTier = (index: number) =>
  WEAK_PHONEME_TIERS[index] ?? {
    label: 'Residual',
    rowClassName: 'border-l-sky-400',
    labelClassName: 'text-sky-300',
    statusClassName: 'text-sky-300/80',
  }
