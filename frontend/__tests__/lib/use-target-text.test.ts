import { describe, expect, it, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useTargetText } from '@/lib/use-target-text'

const fallbackText = 'The rabbit runs fast across the green field.'

vi.mock('@/lib/api', () => ({
  getApiBaseUrl: () => 'http://localhost:8000',
}))

vi.mock('@/lib/home-assessment', () => ({
  fallbackTargetText: 'The rabbit runs fast across the green field.',
}))

beforeEach(() => {
  vi.restoreAllMocks()
})

const mockResponse = (body: unknown, ok = true) =>
  new Response(JSON.stringify(body), {
    status: ok ? 200 : 400,
    headers: { 'Content-Type': 'application/json' },
  })

describe('useTargetText', () => {
  it('starts with fallback target text', () => {
    const { result } = renderHook(() => useTargetText())
    expect(result.current.targetText).toBe(fallbackText)
  })

  it('sets target text on successful fetch', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(mockResponse({ text: 'The cat runs fast' }))

    const { result } = renderHook(() => useTargetText())

    await waitFor(() => {
      result.current.loadTargetText()
    })

    await waitFor(() => {
      expect(result.current.targetText).toBe('The cat runs fast')
    })
  })

  it('falls back on failed fetch', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      mockResponse({ detail: 'Not found' }, false),
    )

    const { result } = renderHook(() => useTargetText())

    await waitFor(() => {
      result.current.loadTargetText()
    })

    await waitFor(() => {
      expect(result.current.targetText).toBe(fallbackText)
    })
  })

  it('handles network failure gracefully', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useTargetText())

    await waitFor(() => {
      result.current.loadTargetText()
    })

    await waitFor(() => {
      expect(result.current.targetText).toBe(fallbackText)
    })
  })

  it('exports loadTargetText function', () => {
    const { result } = renderHook(() => useTargetText())
    expect(typeof result.current.loadTargetText).toBe('function')
  })
})
