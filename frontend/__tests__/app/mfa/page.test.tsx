import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import MultiFactorAuthentication from '@/app/mfa/page'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('@/lib/sound-engine', () => ({
  playSound: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  getApiBaseUrl: () => 'http://localhost:8000',
}))

afterEach(cleanup)

describe('MFA Setup page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders heading', () => {
    render(<MultiFactorAuthentication />)
    expect(screen.getByText('Welcome To Vocalis')).toBeDefined()
  })

  it('shows loading state initially', async () => {
    render(<MultiFactorAuthentication />)
    const loading = await screen.findByText('Preparing MFA...')
    expect(loading).toBeDefined()
  })

  it('renders Continue button', async () => {
    render(<MultiFactorAuthentication />)
    const button = await screen.findByText('Continue')
    expect(button).toBeDefined()
  })

  it('renders step indicator', async () => {
    render(<MultiFactorAuthentication />)
    const step = await screen.findByText('Step 1 Of 2')
    expect(step).toBeDefined()
  })
})
