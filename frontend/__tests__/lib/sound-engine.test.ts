import { describe, expect, it, vi, beforeEach } from 'vitest'
import { decodeAudioData, getAudioContext } from '@/lib/sound-engine'

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('getAudioContext', () => {
  it('returns an AudioContext instance', () => {
    const ctx = getAudioContext()
    expect(ctx).toBeDefined()
    expect(ctx.state).toBe('running')
  })

  it('returns the same instance on subsequent calls', () => {
    const ctx1 = getAudioContext()
    const ctx2 = getAudioContext()
    expect(ctx1).toBe(ctx2)
  })
})

describe('decodeAudioData', () => {
  it('is a function', () => {
    expect(typeof decodeAudioData).toBe('function')
  })
})
