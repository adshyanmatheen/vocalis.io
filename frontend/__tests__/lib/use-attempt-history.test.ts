import { describe, expect, it, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAttemptHistory } from '@/lib/use-attempt-history'

const STORAGE_KEY = 'vocalis-attempt-history'

beforeEach(() => {
  window.localStorage.clear()
})

describe('useAttemptHistory', () => {
  it('starts with empty history', () => {
    const { result } = renderHook(() => useAttemptHistory())
    expect(result.current.attemptHistory).toEqual([])
  })

  it('reads existing history from localStorage', () => {
    const snapshots = [
      { score: 0.8, createdAt: '2024-01-01T00:00:00Z', weakCount: 2, durationSeconds: 30 },
    ]
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshots))

    const { result } = renderHook(() => useAttemptHistory())
    expect(result.current.attemptHistory).toHaveLength(1)
    expect(result.current.attemptHistory[0].score).toBe(0.8)
  })

  it('appends a new attempt', () => {
    const { result } = renderHook(() => useAttemptHistory())

    act(() => {
      result.current.appendAttempt({
        score: 0.9,
        createdAt: '2024-01-02T00:00:00Z',
        weakCount: 0,
        durationSeconds: 25,
      })
    })

    expect(result.current.attemptHistory).toHaveLength(1)
    expect(result.current.attemptHistory[0].score).toBe(0.9)
  })

  it('persists to localStorage on append', () => {
    const { result } = renderHook(() => useAttemptHistory())

    act(() => {
      result.current.appendAttempt({
        score: 0.75,
        createdAt: '2024-01-03T00:00:00Z',
        weakCount: 3,
        durationSeconds: 40,
      })
    })

    const stored = JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? '[]')
    expect(stored).toHaveLength(1)
    expect(stored[0].score).toBe(0.75)
  })

  it('caps history at 8 items', () => {
    const { result } = renderHook(() => useAttemptHistory())

    for (let i = 0; i < 10; i++) {
      act(() => {
        result.current.appendAttempt({
          score: i / 10,
          createdAt: `2024-01-${String(i + 1).padStart(2, '0')}T00:00:00Z`,
          weakCount: i,
          durationSeconds: 30,
        })
      })
    }

    expect(result.current.attemptHistory).toHaveLength(8)
    expect(result.current.attemptHistory[0].score).toBe(0.2)
    expect(result.current.attemptHistory[7].score).toBe(0.9)
  })

  it('handles corrupt localStorage gracefully', () => {
    window.localStorage.setItem(STORAGE_KEY, 'not-valid-json')

    const { result } = renderHook(() => useAttemptHistory())
    expect(result.current.attemptHistory).toEqual([])
  })
})
