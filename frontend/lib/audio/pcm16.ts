import { createMonoSamples } from '@/lib/audio/audioBuffer'

export const REALTIME_SAMPLE_RATE = 16000

const bytesToBase64 = (bytes: Uint8Array) => {
  let binary = ''
  const chunkSize = 0x8000

  for (let index = 0; index < bytes.length; index += chunkSize) {
    const chunk = bytes.subarray(index, index + chunkSize)
    for (let i = 0; i < chunk.length; i++) {
      binary += String.fromCharCode(chunk[i])
    }
  }

  return window.btoa(binary)
}

export const resampleAudioBuffer = async (buffer: AudioBuffer, sampleRate: number) => {
  if (buffer.sampleRate === sampleRate) {
    return buffer
  }

  const duration = buffer.length / buffer.sampleRate
  const frameCount = Math.max(1, Math.round(duration * sampleRate))
  const offlineContext = new OfflineAudioContext(1, frameCount, sampleRate)
  const source = offlineContext.createBufferSource()
  const monoSamples = createMonoSamples(buffer)
  const monoBuffer = offlineContext.createBuffer(1, monoSamples.length, buffer.sampleRate)

  monoBuffer.copyToChannel(monoSamples, 0)
  source.buffer = monoBuffer
  source.connect(offlineContext.destination)
  source.start(0)

  const renderedBuffer = await offlineContext.startRendering()

  return renderedBuffer
}

export const audioBufferToPcm16Bytes = (buffer: AudioBuffer) => {
  const monoSamples = createMonoSamples(buffer)
  const pcmBuffer = new ArrayBuffer(monoSamples.length * 2)
  const view = new DataView(pcmBuffer)

  for (let sampleIndex = 0; sampleIndex < monoSamples.length; sampleIndex += 1) {
    const sample = Math.max(-1, Math.min(1, monoSamples[sampleIndex]))
    view.setInt16(sampleIndex * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
  }

  return new Uint8Array(pcmBuffer)
}

export const chunkPcm16Bytes = (bytes: Uint8Array, sampleRate: number) => {
  const bytesPerSample = 2
  const chunkSize = sampleRate * bytesPerSample
  const chunks: Uint8Array[] = []

  for (let index = 0; index < bytes.length; index += chunkSize) {
    chunks.push(bytes.subarray(index, index + chunkSize))
  }

  return chunks
}

export const pcm16BytesToBase64 = bytesToBase64
