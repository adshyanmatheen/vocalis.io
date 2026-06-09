import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import SignIn from '@/app/sign-in/page'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('@/lib/api', () => ({
  getApiBaseUrl: () => 'http://localhost:8000',
}))

afterEach(cleanup)

describe('SignIn page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders heading', () => {
    render(<SignIn />)
    expect(screen.getByText('Welcome Back To Vocalis')).toBeDefined()
  })

  it('renders username and password inputs', async () => {
    render(<SignIn />)
    const username = await screen.findByPlaceholderText('swift_owl_247')
    const password = await screen.findByPlaceholderText('*********')
    expect(username).toBeDefined()
    expect(password).toBeDefined()
  })

  it('renders Sign In button', async () => {
    render(<SignIn />)
    const button = await screen.findByText('Sign In')
    expect(button).toBeDefined()
  })

  it('renders link to register', async () => {
    render(<SignIn />)
    const link = await screen.findByText('Create Account')
    expect(link).toBeDefined()
  })
})
