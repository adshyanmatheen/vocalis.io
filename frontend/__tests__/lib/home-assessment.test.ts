import { describe, expect, it } from 'vitest'
import {
  buildAssessmentSummary,
  formatMetricNumber,
  formatScore,
  getOverallScorePercent,
  getTimeBasedGreeting,
  getUserInitials,
  getWeakPhonemeTier,
  getWordScoreLabel,
  getWordScoreValue,
  isGenericAssessmentSummary,
  MAX_WEAK_PHONEMES_DISPLAYED,
} from '@/lib/home-assessment'

describe('getUserInitials', () => {
  it('returns V for undefined', () => {
    expect(getUserInitials(undefined)).toBe('V')
  })

  it('returns V for empty string', () => {
    expect(getUserInitials('')).toBe('V')
  })

  it('returns V for whitespace-only string', () => {
    expect(getUserInitials('   ')).toBe('V')
  })

  it('extracts first letter of a single name', () => {
    expect(getUserInitials('matilda')).toBe('M')
  })

  it('extracts initials from first and last name', () => {
    expect(getUserInitials('matilda smith')).toBe('MS')
  })

  it('extracts initials from three names (takes first two)', () => {
    expect(getUserInitials('john jane doe')).toBe('JJ')
  })

  it('uppercases the result', () => {
    expect(getUserInitials('john doe')).toBe('JD')
  })

  it('handles extra whitespace between names', () => {
    expect(getUserInitials('  john   doe  ')).toBe('JD')
  })
})

describe('getOverallScorePercent', () => {
  it('returns 0 for undefined', () => {
    expect(getOverallScorePercent(undefined)).toBe(0)
  })

  it('returns 0 for NaN', () => {
    expect(getOverallScorePercent(NaN)).toBe(0)
  })

  it('converts 0-1 score to percentage', () => {
    expect(getOverallScorePercent(0.85)).toBe(85)
  })

  it('treats >1 as percentage already (divides by 100)', () => {
    expect(getOverallScorePercent(1.5)).toBe(2)
  })

  it('floors at 0', () => {
    expect(getOverallScorePercent(-0.5)).toBe(0)
  })

  it('handles score > 1 as already percentage', () => {
    expect(getOverallScorePercent(85)).toBe(85)
  })

  it('rounds to nearest integer', () => {
    expect(getOverallScorePercent(0.856)).toBe(86)
  })
})

describe('formatScore', () => {
  it('appends % suffix', () => {
    expect(formatScore(0.75)).toBe('75%')
  })

  it('returns 0% for undefined', () => {
    expect(formatScore(undefined)).toBe('0%')
  })
})

describe('formatMetricNumber', () => {
  it('formats number with default digits', () => {
    expect(formatMetricNumber(3.14159)).toBe('3.1')
  })

  it('formats number with custom digits', () => {
    expect(formatMetricNumber(3.14159, 3)).toBe('3.142')
  })

  it('returns -- for non-number', () => {
    expect(formatMetricNumber(undefined)).toBe('--')
  })

  it('returns -- for NaN', () => {
    expect(formatMetricNumber(NaN)).toBe('--')
  })

  it('returns -- for string', () => {
    expect(formatMetricNumber('hello')).toBe('--')
  })
})

describe('getTimeBasedGreeting', () => {
  it('returns a greeting string', () => {
    const greeting = getTimeBasedGreeting()
    expect(['Good Morning', 'Good Afternoon', 'Good Evening', 'Good Night']).toContain(greeting)
  })
})

describe('getWeakPhonemeTier', () => {
  it('returns Primary for index 0', () => {
    const tier = getWeakPhonemeTier(0)
    expect(tier.label).toBe('Primary')
    expect(tier.rowClassName).toContain('red')
  })

  it('returns Secondary for index 1', () => {
    const tier = getWeakPhonemeTier(1)
    expect(tier.label).toBe('Secondary')
    expect(tier.rowClassName).toContain('amber')
  })

  it('returns Tertiary for index 2', () => {
    const tier = getWeakPhonemeTier(2)
    expect(tier.label).toBe('Tertiary')
    expect(tier.rowClassName).toContain('yellow')
  })

  it('returns Residual for index beyond tiers', () => {
    const tier = getWeakPhonemeTier(5)
    expect(tier.label).toBe('Residual')
    expect(tier.rowClassName).toContain('sky')
  })
})

describe('MAX_WEAK_PHONEMES_DISPLAYED', () => {
  it('is 7 (3 tiers + 4 residual)', () => {
    expect(MAX_WEAK_PHONEMES_DISPLAYED).toBe(7)
  })
})

describe('getWordScoreValue', () => {
  it('picks weighted_score first', () => {
    expect(getWordScoreValue({ weighted_score: 0.9, score: 0.8 } as any)).toBe(0.9)
  })

  it('falls back to score', () => {
    expect(getWordScoreValue({ score: 0.8 } as any)).toBe(0.8)
  })

  it('falls back to average_confidence', () => {
    expect(getWordScoreValue({ average_confidence: 0.7 } as any)).toBe(0.7)
  })

  it('returns 0 when no numeric field found', () => {
    expect(getWordScoreValue({ word: 'hello' } as any)).toBe(0)
  })

  it('parses string candidates', () => {
    expect(getWordScoreValue({ score: '0.85' } as any)).toBe(0.85)
  })
})

describe('getWordScoreLabel', () => {
  it('returns word field', () => {
    expect(getWordScoreLabel({ word: 'hello' } as any)).toBe('hello')
  })

  it('falls back to text field', () => {
    expect(getWordScoreLabel({ text: 'world' } as any)).toBe('world')
  })

  it('falls back to Word', () => {
    expect(getWordScoreLabel({} as any)).toBe('Word')
  })
})

describe('isGenericAssessmentSummary', () => {
  it('returns true for undefined', () => {
    expect(isGenericAssessmentSummary(undefined)).toBe(true)
  })

  it('returns true for empty string', () => {
    expect(isGenericAssessmentSummary('')).toBe(true)
  })

  it('returns true for the default summary', () => {
    expect(isGenericAssessmentSummary('Realtime pronunciation assessment completed.')).toBe(true)
  })

  it('returns true for variants', () => {
    expect(isGenericAssessmentSummary('Realtime assessment complete: your score is 85%.')).toBe(
      true,
    )
  })

  it('returns false for custom summaries', () => {
    expect(isGenericAssessmentSummary('Great improvement on your /r/ sound!')).toBe(false)
  })
})

describe('buildAssessmentSummary', () => {
  it('builds high-score summary with no weak sounds', () => {
    const result = buildAssessmentSummary({
      score: 0.85,
      performanceBand: 'Strong',
      weakPhonemes: [],
      weakestWords: [],
      trendDelta: null,
    })
    expect(result).toContain('85%')
    expect(result).toContain('strong')
  })

  it('includes trend delta when improving', () => {
    const result = buildAssessmentSummary({
      score: 0.85,
      performanceBand: 'Strong',
      weakPhonemes: [],
      weakestWords: [],
      trendDelta: 0.05,
    })
    expect(result).toContain('Up 5')
  })

  it('includes trend delta when declining', () => {
    const result = buildAssessmentSummary({
      score: 0.85,
      performanceBand: 'Strong',
      weakPhonemes: [],
      weakestWords: [],
      trendDelta: -0.03,
    })
    expect(result).toContain('Down 3')
  })

  it('includes weak phoneme focus for scores below 75', () => {
    const result = buildAssessmentSummary({
      score: 0.6,
      performanceBand: 'On Track',
      weakPhonemes: ['r', 'l'],
      weakestWords: [{ word: 'rabbit' }],
      trendDelta: null,
    })
    expect(result).toContain('60%')
    expect(result).toContain('/r/')
    expect(result).toContain('/l/')
  })

  it('mentions weakest word', () => {
    const result = buildAssessmentSummary({
      score: 0.5,
      performanceBand: 'Fair',
      weakPhonemes: ['th'],
      weakestWords: [{ word: 'thought' }],
      trendDelta: null,
    })
    expect(result).toContain('thought')
  })
})
