import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import MFAVerification from '@/app/mfa/verify/page'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams('mode=setup'),
}))

vi.mock('@/lib/sound-engine', () => ({
  playSound: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  getApiBaseUrl: () => 'http://localhost:8000',
}))

afterEach(cleanup)

describe('MFA Verification page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders heading', () => {
    render(<MFAVerification />)
    expect(screen.getByText('Welcome To Vocalis')).toBeDefined()
  })

  it('renders step indicator', async () => {
    render(<MFAVerification />)
    const step = await screen.findByText('Step 2 Of 2')
    expect(step).toBeDefined()
  })

  it('renders Verify button', async () => {
    render(<MFAVerification />)
    const button = await screen.findByText('Verify')
    expect(button).toBeDefined()
  })

  it('renders back link to MFA setup', async () => {
    render(<MFAVerification />)
    const backLink = await screen.findByLabelText('Back To MFA Setup')
    expect(backLink).toBeDefined()
    expect(backLink.getAttribute('href')).toBe('/mfa')
  })
})
