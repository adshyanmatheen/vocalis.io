import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import Home from '@/app/home/page'

vi.mock('@/components/auth-provider', () => ({
  useAuth: () => ({
    user: { id: 1, name: 'Test', username: 'test' },
    loading: false,
    refreshAuth: vi.fn(),
  }),
  AuthProvider: ({ children }: any) => <>{children}</>,
}))

vi.mock('@/lib/use-require-auth', () => ({
  useRequireAuth: () => ({
    user: { id: 1, name: 'Test User', username: 'testuser' },
    loading: false,
  }),
}))

vi.mock('@/lib/home-assessment', () => ({
  getTimeBasedGreeting: () => 'Good Morning',
  getUserInitials: (name?: string) => name?.charAt(0)?.toUpperCase() ?? 'V',
  formatScore: (s?: number) => `${Math.round((s ?? 0) * 100)}%`,
  formatMetricNumber: (n?: number) => n?.toFixed(1) ?? '--',
  getOverallScorePercent: (s?: number) => Math.round((s ?? 0) * 100),
  getWeakPhonemeTier: (i: number) => ({
    label: ['Primary', 'Secondary', 'Tertiary', 'Residual'][i] ?? 'Residual',
    rowClassName: '',
  }),
  getWordScoreLabel: (w: any) => w?.word ?? 'Word',
  getWordScoreValue: (w: any) => w?.score ?? 0,
  MAX_WEAK_PHONEMES_DISPLAYED: 7,
  fallbackTargetText: 'The rabbit runs fast across the green field.',
  dotMeters: Array.from({ length: 8 }),
  VoiceState: {} as any,
}))

vi.mock('@/lib/use-target-text', () => ({
  useTargetText: () => ({ targetText: 'The rabbit runs fast', loadTargetText: vi.fn() }),
}))

vi.mock('@/lib/use-attempt-history', () => ({
  useAttemptHistory: () => ({ attemptHistory: [], appendAttempt: vi.fn() }),
}))

vi.mock('@/lib/use-enriched-assessment-result', () => ({
  useEnrichedAssessmentResult: () => null,
}))

vi.mock('@/lib/realtime-assessment', () => ({
  getModelHealth: vi.fn(),
  getModelHealthMessage: () => null,
  submitRealtimeAssessment: vi.fn(),
}))

vi.mock('@/lib/audio/preprocess', () => ({
  preprocessRecordedAudio: vi.fn(),
}))

vi.mock('@/lib/sound-engine', () => ({
  playSound: vi.fn(),
}))

vi.mock('@/lib/error-005', () => ({ error005Sound: { dataUri: '' } }))
vi.mock('@/lib/success-chime', () => ({ successChimeSound: { dataUri: '' } }))
vi.mock('@/lib/switch-001', () => ({ switch001Sound: { dataUri: '' } }))
vi.mock('@/lib/switch-off', () => ({ switchOffSound: { dataUri: '' } }))
vi.mock('@/lib/switch-on', () => ({ switchOnSound: { dataUri: '' } }))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}))

vi.mock('@/components/ui/audio-lines', () => ({
  AudioLinesIcon: ({ ref: _ref, ...props }: any) => <div data-testid="audio-lines" {...props} />,
}))

vi.mock('@/components/ui/grip', () => ({
  GripIcon: ({ ref: _ref, ...props }: any) => <div data-testid="grip-icon" {...props} />,
}))

vi.mock('@/components/ai-elements/audio-player', () => ({
  AudioPlayer: ({ children }: any) => <div data-testid="audio-player">{children}</div>,
  AudioPlayerControlBar: ({ children }: any) => <div>{children}</div>,
  AudioPlayerDurationDisplay: () => <span />,
  AudioPlayerElement: ({ children }: any) => <div>{children}</div>,
  AudioPlayerPlayButton: () => <button>Play</button>,
  AudioPlayerTimeDisplay: () => <span />,
  AudioPlayerTimeRange: () => <div />,
  AudioPlayerVolumeRange: () => <div />,
}))

afterEach(cleanup)

describe('Home page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders greeting with user name', async () => {
    render(<Home />)
    const greeting = await screen.findByText('Good Morning Test User')
    expect(greeting).toBeDefined()
  })

  it('renders account link', async () => {
    render(<Home />)
    const accountLink = await screen.findByLabelText('Open account')
    expect(accountLink).toBeDefined()
  })

  it('renders target text', async () => {
    render(<Home />)
    const text = await screen.findByText('The rabbit runs fast')
    expect(text).toBeDefined()
  })

  it('renders as main element', () => {
    render(<Home />)
    const main = document.querySelector('main')
    expect(main).toBeDefined()
  })
})
