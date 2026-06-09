import { calculatePeak, calculateRms, createMonoSamples } from '@/lib/audio/audioBuffer'

export type AqgOptions = {
  speechDuration: number
  speechRatio: number
  noiseFloor: number
}

export type AqgResult = {
  passed: boolean
  issues: string[]
}

export const runAudioQualityGate = (buffer: AudioBuffer, options: AqgOptions): AqgResult => {
  const monoSamples = createMonoSamples(buffer)
  const rms = calculateRms(monoSamples)
  const peak = calculatePeak(monoSamples)
  let clippedSamples = 0

  for (let index = 0; index < monoSamples.length; index += 1) {
    if (Math.abs(monoSamples[index]) >= 0.99) {
      clippedSamples += 1
    }
  }

  const clippedRatio = monoSamples.length > 0 ? clippedSamples / monoSamples.length : 0
  const clarityScore = options.noiseFloor > 0 ? rms / options.noiseFloor : rms / 0.01
  const issues: string[] = []
  const minimumSpeechDuration = 0.35
  const minimumSpeechRatio = 0.18

  if (options.speechDuration < minimumSpeechDuration) {
    issues.push('Recording is too short. Please say the full phrase clearly.')
  }

  if (options.speechRatio < minimumSpeechRatio) {
    issues.push('Too much silence was detected. Please speak more consistently.')
  }

  if (rms < 0.03) {
    issues.push('Recording is too quiet. Please speak a little louder.')
  }

  if (peak > 0.995 && clippedRatio > 0.002) {
    issues.push('Recording is clipping. Please move slightly away from the microphone.')
  }

  if (clarityScore < 2) {
    issues.push('Recording is not clear enough. Please reduce background noise and try again.')
  }

  return {
    passed: issues.length === 0,
    issues,
  }
}
