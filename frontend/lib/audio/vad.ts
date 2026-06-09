import { calculateRms, createMonoAudioBuffer, createMonoSamples } from '@/lib/audio/audioBuffer'

export type VadResult = {
  trimmedBuffer: AudioBuffer | null
  speechDuration: number
  speechRatio: number
  noiseFloor: number
  speechThreshold: number
}

export const runVoiceActivityDetection = (
  audioContext: AudioContext,
  buffer: AudioBuffer,
): VadResult => {
  const monoSamples = createMonoSamples(buffer)
  const frameSize = Math.max(1, Math.floor(buffer.sampleRate * 0.02))
  const frameCount = Math.ceil(monoSamples.length / frameSize)
  const frameEnergy: number[] = []

  for (let frameIndex = 0; frameIndex < frameCount; frameIndex += 1) {
    const start = frameIndex * frameSize
    const end = Math.min(start + frameSize, monoSamples.length)
    const frame = monoSamples.subarray(start, end)
    frameEnergy.push(calculateRms(frame))
  }

  const sortedEnergy = [...frameEnergy].sort((left, right) => left - right)
  const noiseFloor = sortedEnergy[Math.floor(sortedEnergy.length * 0.2)] ?? 0
  const speechThreshold = Math.max(0.012, noiseFloor * 2.2)
  const speechMask = Array(frameCount).fill(false)

  for (let frameIndex = 0; frameIndex < frameCount; frameIndex += 1) {
    if (frameEnergy[frameIndex] >= speechThreshold) {
      for (
        let paddedIndex = Math.max(0, frameIndex - 1);
        paddedIndex <= Math.min(frameCount - 1, frameIndex + 1);
        paddedIndex += 1
      ) {
        speechMask[paddedIndex] = true
      }
    }
  }

  const speechSampleCount = speechMask.reduce(
    (total, hasSpeech) => total + (hasSpeech ? frameSize : 0),
    0,
  )

  if (speechSampleCount === 0) {
    return {
      trimmedBuffer: null,
      speechDuration: 0,
      speechRatio: 0,
      noiseFloor,
      speechThreshold,
    }
  }

  const trimmedSamples = new Float32Array(Math.min(speechSampleCount, monoSamples.length))
  let writeOffset = 0

  for (let frameIndex = 0; frameIndex < frameCount; frameIndex += 1) {
    if (!speechMask[frameIndex]) {
      continue
    }

    const start = frameIndex * frameSize
    const end = Math.min(start + frameSize, monoSamples.length)
    trimmedSamples.set(monoSamples.subarray(start, end), writeOffset)
    writeOffset += end - start
  }

  const finalSamples = trimmedSamples.subarray(0, writeOffset)

  return {
    trimmedBuffer: createMonoAudioBuffer(audioContext, finalSamples, buffer.sampleRate),
    speechDuration: finalSamples.length / buffer.sampleRate,
    speechRatio: finalSamples.length / monoSamples.length,
    noiseFloor,
    speechThreshold,
  }
}
