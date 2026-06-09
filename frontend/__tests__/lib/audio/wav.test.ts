import { describe, expect, it } from 'vitest'
import { audioBufferToWav } from '@/lib/audio/wav'

function createMockBuffer(samples: Float32Array, sampleRate = 16000): AudioBuffer {
  return {
    length: samples.length,
    sampleRate,
    numberOfChannels: 1,
    getChannelData: () => samples,
  } as unknown as AudioBuffer
}

describe('audioBufferToWav', () => {
  it('returns a Blob with audio/wav type', () => {
    const samples = new Float32Array(16000)
    const buffer = createMockBuffer(samples)
    const blob = audioBufferToWav(buffer)
    expect(blob).toBeInstanceOf(Blob)
    expect(blob.type).toBe('audio/wav')
  })

  it('produces correct WAV header size (44 bytes + data)', () => {
    const samples = new Float32Array(100)
    const buffer = createMockBuffer(samples)
    const blob = audioBufferToWav(buffer)
    expect(blob.size).toBe(44 + 100 * 2)
  })

  it('clamps samples outside [-1, 1]', () => {
    const samples = new Float32Array([2.0, -2.0, 0.5])
    const buffer = createMockBuffer(samples)
    const blob = audioBufferToWav(buffer)
    expect(blob.size).toBe(44 + 3 * 2)
  })

  it('writes RIFF header correctly', async () => {
    const samples = new Float32Array(10)
    const buffer = createMockBuffer(samples)
    const blob = audioBufferToWav(buffer)
    const header = await blob.slice(0, 4).text()
    expect(header).toBe('RIFF')
  })

  it('writes WAVE format marker', async () => {
    const samples = new Float32Array(10)
    const buffer = createMockBuffer(samples)
    const blob = audioBufferToWav(buffer)
    const fmt = await blob.slice(8, 12).text()
    expect(fmt).toBe('WAVE')
  })
})
