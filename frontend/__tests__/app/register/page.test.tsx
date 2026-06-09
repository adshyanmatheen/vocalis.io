import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import Register from '@/app/register/page'

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

describe('Register page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders heading', () => {
    render(<Register />)
    expect(screen.getByText('Welcome To Vocalis')).toBeDefined()
  })

  it('renders name and password inputs', async () => {
    render(<Register />)
    const name = await screen.findByPlaceholderText('Matilda Smith')
    const password = await screen.findByPlaceholderText('*********')
    expect(name).toBeDefined()
    expect(password).toBeDefined()
  })

  it('renders Create Account button', async () => {
    render(<Register />)
    const button = await screen.findByText('Create Account')
    expect(button).toBeDefined()
  })

  it('renders link to sign in', async () => {
    render(<Register />)
    const link = await screen.findByText('Sign In')
    expect(link).toBeDefined()
  })
})
