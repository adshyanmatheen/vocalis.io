import { describe, expect, it } from 'vitest'
import { runVoiceActivityDetection } from '@/lib/audio/vad'

function createMockBuffer(samples: Float32Array, sampleRate = 16000): AudioBuffer {
  return {
    length: samples.length,
    sampleRate,
    numberOfChannels: 1,
    getChannelData: () => samples,
  } as unknown as AudioBuffer
}

function createMockAudioContext(): AudioContext {
  return {
    createBuffer: (channels: number, length: number, sampleRate: number) =>
      ({
        length,
        sampleRate,
        numberOfChannels: channels,
        getChannelData: () => new Float32Array(length),
      }) as unknown as AudioBuffer,
  } as unknown as AudioContext
}

describe('runVoiceActivityDetection', () => {
  it('returns result with expected shape for silent input', () => {
    const buffer = createMockBuffer(new Float32Array(16000))
    const result = runVoiceActivityDetection(createMockAudioContext(), buffer)
    expect(result).toHaveProperty('trimmedBuffer')
    expect(result).toHaveProperty('speechDuration')
    expect(result).toHaveProperty('speechRatio')
    expect(result).toHaveProperty('noiseFloor')
    expect(result).toHaveProperty('speechThreshold')
  })
})
