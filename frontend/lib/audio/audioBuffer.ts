export const createMonoSamples = (buffer: AudioBuffer) => {
  const channelData = Array.from({ length: buffer.numberOfChannels }, (_, index) =>
    buffer.getChannelData(index),
  )
  const monoSamples = new Float32Array(buffer.length)

  for (let sampleIndex = 0; sampleIndex < buffer.length; sampleIndex += 1) {
    let total = 0

    for (let channelIndex = 0; channelIndex < channelData.length; channelIndex += 1) {
      total += channelData[channelIndex][sampleIndex]
    }

    monoSamples[sampleIndex] = total / channelData.length
  }

  return monoSamples
}

export const calculateRms = (samples: ArrayLike<number>) => {
  if (samples.length === 0) {
    return 0
  }

  let sum = 0

  for (let index = 0; index < samples.length; index += 1) {
    sum += samples[index] * samples[index]
  }

  return Math.sqrt(sum / samples.length)
}

export const calculatePeak = (samples: ArrayLike<number>) => {
  let peak = 0

  for (let index = 0; index < samples.length; index += 1) {
    peak = Math.max(peak, Math.abs(samples[index]))
  }

  return peak
}

export const createMonoAudioBuffer = (
  audioContext: AudioContext,
  samples: ArrayLike<number>,
  sampleRate: number,
) => {
  const normalizedSamples =
    samples instanceof Float32Array ? new Float32Array(samples) : Float32Array.from(samples)
  const nextBuffer = audioContext.createBuffer(1, normalizedSamples.length, sampleRate)
  nextBuffer.copyToChannel(normalizedSamples, 0)
  return nextBuffer
}
