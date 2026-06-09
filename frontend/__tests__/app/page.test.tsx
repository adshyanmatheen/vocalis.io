import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import HomePage from '@/app/page'

vi.mock('@/components/auth-provider', () => ({
  useAuth: () => ({ user: null, loading: false, refreshAuth: vi.fn() }),
}))

vi.mock('@/lib/sound-engine', () => ({
  playSound: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

afterEach(cleanup)

describe('HomePage (landing)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders welcome text', () => {
    render(<HomePage />)
    expect(screen.getByText('Welcome To Vocalis')).toBeDefined()
  })

  it('renders Get Started button', async () => {
    render(<HomePage />)
    const button = await screen.findByText('Get Started')
    expect(button).toBeDefined()
  })

  it('renders tagline', async () => {
    render(<HomePage />)
    const tagline = await screen.findByText(
      'Your Adaptive Explainable AI Pronunciation Training Companion',
    )
    expect(tagline).toBeDefined()
  })

  it('renders as main element', () => {
    render(<HomePage />)
    const main = document.querySelector('main')
    expect(main).toBeDefined()
  })
})
