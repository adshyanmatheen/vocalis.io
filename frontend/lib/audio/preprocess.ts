import { runAudioQualityGate } from '@/lib/audio/aqg'
import { runVoiceActivityDetection } from '@/lib/audio/vad'
import { audioBufferToWav } from '@/lib/audio/wav'

export type PreprocessedAudio = {
  originalBuffer: AudioBuffer
  trimmedBuffer: AudioBuffer
  wavBlob: Blob
  speechDuration: number
  speechRatio: number
  issues: string[]
}

export const preprocessRecordedAudio = async (audioBlob: Blob) => {
  const audioContext = new AudioContext()

  try {
    const audioData = await audioBlob.arrayBuffer()
    const originalBuffer = await audioContext.decodeAudioData(audioData)
    const vadResult = runVoiceActivityDetection(audioContext, originalBuffer)

    if (!vadResult.trimmedBuffer) {
      return {
        originalBuffer,
        trimmedBuffer: null,
        wavBlob: null,
        speechDuration: vadResult.speechDuration,
        speechRatio: vadResult.speechRatio,
        issues: ['No clear speech was detected. Please try again.'],
      }
    }

    const qualityResult = runAudioQualityGate(vadResult.trimmedBuffer, {
      speechDuration: vadResult.speechDuration,
      speechRatio: vadResult.speechRatio,
      noiseFloor: vadResult.noiseFloor,
    })

    return {
      originalBuffer,
      trimmedBuffer: vadResult.trimmedBuffer,
      wavBlob: audioBufferToWav(vadResult.trimmedBuffer),
      speechDuration: vadResult.speechDuration,
      speechRatio: vadResult.speechRatio,
      issues: qualityResult.issues,
    }
  } finally {
    await audioContext.close()
  }
}
