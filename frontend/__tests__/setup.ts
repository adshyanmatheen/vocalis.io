Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
})

class MockIntersectionObserver {
  readonly root: Element | null = null
  readonly rootMargin: string = ''
  readonly thresholds: ReadonlyArray<number> = []
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords(): IntersectionObserverEntry[] {
    return []
  }
}
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
})

class MockResizeObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}
Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: MockResizeObserver,
})

class MockAudioContext {
  state: string = 'running'
  sampleRate: number = 48000
  destination: Record<string, unknown> = {}
  currentTime: number = 0
  constructor() {}
  resume() {
    return Promise.resolve()
  }
  close() {
    return Promise.resolve()
  }
  createBufferSource() {
    return {
      buffer: null,
      playbackRate: { value: 1 },
      connect: () => {},
      start: () => {},
      stop: () => {},
      onended: null,
    }
  }
  createGain() {
    return { gain: { value: 1 }, connect: () => {} }
  }
  decodeAudioData(arrayBuffer: ArrayBuffer) {
    return Promise.resolve({
      duration: 1,
      length: 48000,
      sampleRate: 48000,
      numberOfChannels: 1,
      getChannelData: () => new Float32Array(48000),
      copyFromChannel: () => {},
      copyToChannel: () => {},
    } as unknown as AudioBuffer)
  }
  createBuffer(channels: number, length: number, sampleRate: number) {
    return {
      length,
      sampleRate,
      numberOfChannels: channels,
      getChannelData: () => new Float32Array(length),
    } as unknown as AudioBuffer
  }
}
Object.defineProperty(window, 'AudioContext', {
  writable: true,
  value: MockAudioContext,
})

const localStorageStore: Record<string, string> = {}
Object.defineProperty(window, 'localStorage', {
  writable: true,
  value: {
    getItem: (key: string) => localStorageStore[key] ?? null,
    setItem: (key: string, value: string) => {
      localStorageStore[key] = value
    },
    removeItem: (key: string) => {
      delete localStorageStore[key]
    },
    clear: () => {
      Object.keys(localStorageStore).forEach((key) => {
        delete localStorageStore[key]
      })
    },
    get length() {
      return Object.keys(localStorageStore).length
    },
    key: (index: number) => Object.keys(localStorageStore)[index] ?? null,
  },
})
