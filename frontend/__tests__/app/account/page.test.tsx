import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import Account from '@/app/account/page'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}))

vi.mock('@/lib/sound-engine', () => ({
  playSound: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  fetchAccountSummary: vi.fn().mockResolvedValue(null),
  logoutUser: vi.fn(),
}))

vi.mock('@/lib/use-require-auth', () => ({
  useRequireAuth: () => ({
    user: { id: 1, name: 'Test User', username: 'testuser' },
    loading: false,
  }),
}))

afterEach(cleanup)

describe('Account page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders heading', () => {
    render(<Account />)
    expect(screen.getByText('Welcome To Your Personal Vocalis Account')).toBeDefined()
  })

  it('renders user name', async () => {
    render(<Account />)
    const name = await screen.findByText('Test User')
    expect(name).toBeDefined()
  })

  it('renders Sign Out button', async () => {
    render(<Account />)
    const button = await screen.findByText('Sign Out')
    expect(button).toBeDefined()
  })

  it('renders back link to home', async () => {
    render(<Account />)
    const backLink = await screen.findByLabelText('Back To Home')
    expect(backLink).toBeDefined()
    expect(backLink.getAttribute('href')).toBe('/home')
  })

  it('renders stat placeholders', async () => {
    render(<Account />)
    const attempts = await screen.findByText('Attempts')
    const average = await screen.findByText('Average')
    expect(attempts).toBeDefined()
    expect(average).toBeDefined()
  })
})
