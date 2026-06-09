import { describe, expect, it } from 'vitest'
import { calculatePeak, calculateRms, createMonoSamples } from '@/lib/audio/audioBuffer'

function createMockBuffer(channels: number, length: number, sampleRate = 16000): AudioBuffer {
  const buffer = {
    length,
    sampleRate,
    numberOfChannels: channels,
    getChannelData: (channel: number) => {
      const data = new Float32Array(length)
      for (let i = 0; i < length; i++) {
        data[i] =
          channel === 0
            ? Math.sin((i / length) * Math.PI * 2)
            : Math.cos((i / length) * Math.PI * 2)
      }
      return data
    },
  } as unknown as AudioBuffer
  return buffer
}

describe('createMonoSamples', () => {
  it('averages multiple channels into one', () => {
    const buffer = createMockBuffer(2, 100)
    const mono = createMonoSamples(buffer)
    expect(mono).toBeInstanceOf(Float32Array)
    expect(mono.length).toBe(100)
  })

  it('handles single channel', () => {
    const buffer = createMockBuffer(1, 50)
    const mono = createMonoSamples(buffer)
    expect(mono.length).toBe(50)
  })
})

describe('calculateRms', () => {
  it('returns 0 for empty array', () => {
    expect(calculateRms([])).toBe(0)
  })

  it('returns 0 for all zeros', () => {
    expect(calculateRms(new Float32Array(10))).toBe(0)
  })

  it('computes RMS for non-zero samples', () => {
    const samples = new Float32Array([0.5, 0.5, 0.5, 0.5])
    const rms = calculateRms(samples)
    expect(rms).toBeCloseTo(0.5, 5)
  })

  it('computes RMS for alternating signs', () => {
    const samples = new Float32Array([1, -1, 1, -1])
    const rms = calculateRms(samples)
    expect(rms).toBeCloseTo(1, 5)
  })
})

describe('calculatePeak', () => {
  it('returns 0 for all zeros', () => {
    expect(calculatePeak(new Float32Array(10))).toBe(0)
  })

  it('finds the maximum absolute value', () => {
    const samples = new Float32Array([0.1, -0.5, 0.3, 0.9, -0.2])
    expect(calculatePeak(samples)).toBeCloseTo(0.9, 5)
  })

  it('handles negative peak', () => {
    const samples = new Float32Array([0.1, -0.95, 0.3])
    expect(calculatePeak(samples)).toBeCloseTo(0.95, 5)
  })
})
