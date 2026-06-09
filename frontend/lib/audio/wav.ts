import { createMonoSamples } from '@/lib/audio/audioBuffer'

const writeString = (view: DataView, offset: number, value: string) => {
  for (let index = 0; index < value.length; index += 1) {
    view.setUint8(offset + index, value.charCodeAt(index))
  }
}

export const audioBufferToWav = (buffer: AudioBuffer) => {
  const sampleRate = buffer.sampleRate
  const monoSamples = createMonoSamples(buffer)
  const wavBuffer = new ArrayBuffer(44 + monoSamples.length * 2)
  const view = new DataView(wavBuffer)

  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + monoSamples.length * 2, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(view, 36, 'data')
  view.setUint32(40, monoSamples.length * 2, true)

  let offset = 44

  for (let sampleIndex = 0; sampleIndex < monoSamples.length; sampleIndex += 1) {
    const sample = Math.max(-1, Math.min(1, monoSamples[sampleIndex]))
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
    offset += 2
  }

  return new Blob([wavBuffer], { type: 'audio/wav' })
}
