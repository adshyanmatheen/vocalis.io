import { describe, expect, it, vi } from 'vitest'
import { preprocessRecordedAudio } from '@/lib/audio/preprocess'

vi.mock('@/lib/audio/vad', () => ({
  runVoiceActivityDetection: vi.fn(() => ({
    trimmedBuffer: null,
    speechDuration: 0.1,
    speechRatio: 0.05,
    noiseFloor: 0.01,
  })),
}))

vi.mock('@/lib/audio/wav', () => ({
  audioBufferToWav: vi.fn(() => new Blob(['mock-wav'], { type: 'audio/wav' })),
}))

vi.mock('@/lib/audio/aqg', () => ({
  runAudioQualityGate: vi.fn(() => ({
    passed: false,
    issues: ['Recording is too short.'],
  })),
}))

function createMockBlob(): Blob {
  return new Blob([new Uint8Array(100)], { type: 'audio/webm' })
}

describe('preprocessRecordedAudio', () => {
  it('returns issue when no speech detected', async () => {
    const result = await preprocessRecordedAudio(createMockBlob())
    expect(result.issues).toContain('No clear speech was detected. Please try again.')
    expect(result.wavBlob).toBeNull()
  })
})
