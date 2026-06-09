import { describe, expect, it } from 'vitest'
import { runAudioQualityGate } from '@/lib/audio/aqg'

function createMockBuffer(samples: Float32Array, sampleRate = 16000): AudioBuffer {
  return {
    length: samples.length,
    sampleRate,
    numberOfChannels: 1,
    getChannelData: () => samples,
  } as unknown as AudioBuffer
}

describe('runAudioQualityGate', () => {
  it('passes clean audio with good speech', () => {
    const samples = new Float32Array(16000)
    for (let i = 0; i < 16000; i++) {
      samples[i] = Math.sin((i / 16000) * Math.PI * 2 * 200) * 0.3
    }
    const buffer = createMockBuffer(samples)
    const result = runAudioQualityGate(buffer, {
      speechDuration: 1.0,
      speechRatio: 0.8,
      noiseFloor: 0.01,
    })
    expect(result.passed).toBe(true)
    expect(result.issues).toHaveLength(0)
  })

  it('fails for too-short speech', () => {
    const buffer = createMockBuffer(new Float32Array(100))
    const result = runAudioQualityGate(buffer, {
      speechDuration: 0.1,
      speechRatio: 0.5,
      noiseFloor: 0.01,
    })
    expect(result.issues.some((i) => i.includes('too short'))).toBe(true)
  })

  it('fails for too much silence', () => {
    const buffer = createMockBuffer(new Float32Array(16000))
    const result = runAudioQualityGate(buffer, {
      speechDuration: 1.0,
      speechRatio: 0.05,
      noiseFloor: 0.01,
    })
    expect(result.issues.some((i) => i.includes('silence'))).toBe(true)
  })

  it('fails for quiet audio', () => {
    const buffer = createMockBuffer(new Float32Array(16000))
    const result = runAudioQualityGate(buffer, {
      speechDuration: 1.0,
      speechRatio: 0.8,
      noiseFloor: 0.01,
    })
    expect(result.issues.some((i) => i.includes('too quiet'))).toBe(true)
  })

  it('detects clipping', () => {
    const samples = new Float32Array(16000)
    for (let i = 0; i < 16000; i++) {
      samples[i] = i % 2 === 0 ? 0.999 : 0.0
    }
    const buffer = createMockBuffer(samples)
    const result = runAudioQualityGate(buffer, {
      speechDuration: 1.0,
      speechRatio: 0.8,
      noiseFloor: 0.01,
    })
    expect(result.issues.some((i) => i.includes('clipping'))).toBe(true)
  })
})
