import { describe, expect, it } from 'vitest'
import { audioBufferToPcm16Bytes, chunkPcm16Bytes, REALTIME_SAMPLE_RATE } from '@/lib/audio/pcm16'

function createMockBuffer(samples: Float32Array, sampleRate = 16000): AudioBuffer {
  return {
    length: samples.length,
    sampleRate,
    numberOfChannels: 1,
    getChannelData: () => samples,
  } as unknown as AudioBuffer
}

describe('audioBufferToPcm16Bytes', () => {
  it('converts samples to PCM16 Uint8Array', () => {
    const buffer = createMockBuffer(new Float32Array([0.0, 0.5, -0.5, 1.0, -1.0]))
    const bytes = audioBufferToPcm16Bytes(buffer)
    expect(bytes).toBeInstanceOf(Uint8Array)
    expect(bytes.length).toBe(5 * 2)
  })

  it('outputs correct byte size', () => {
    const buffer = createMockBuffer(new Float32Array(100))
    const bytes = audioBufferToPcm16Bytes(buffer)
    expect(bytes.length).toBe(200)
  })

  it('clamps extreme values', () => {
    const buffer = createMockBuffer(new Float32Array([2.0, -2.0]))
    const bytes = audioBufferToPcm16Bytes(buffer)
    expect(bytes.length).toBe(4)
  })
})

describe('chunkPcm16Bytes', () => {
  it('splits bytes into one-second chunks', () => {
    const bytes = new Uint8Array(REALTIME_SAMPLE_RATE * 2 * 3)
    const chunks = chunkPcm16Bytes(bytes, REALTIME_SAMPLE_RATE)
    expect(chunks.length).toBe(3)
    chunks.forEach((chunk) => {
      expect(chunk.length).toBe(REALTIME_SAMPLE_RATE * 2)
    })
  })

  it('handles partial last chunk', () => {
    const bytes = new Uint8Array(REALTIME_SAMPLE_RATE * 2 + 100)
    const chunks = chunkPcm16Bytes(bytes, REALTIME_SAMPLE_RATE)
    expect(chunks.length).toBe(2)
    expect(chunks[1].length).toBe(100)
  })

  it('returns single chunk for short audio', () => {
    const bytes = new Uint8Array(100)
    const chunks = chunkPcm16Bytes(bytes, REALTIME_SAMPLE_RATE)
    expect(chunks.length).toBe(1)
    expect(chunks[0].length).toBe(100)
  })

  it('returns empty array for empty input', () => {
    const chunks = chunkPcm16Bytes(new Uint8Array(0), REALTIME_SAMPLE_RATE)
    expect(chunks.length).toBe(0)
  })
})
