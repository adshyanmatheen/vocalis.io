import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, cleanup } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/components/auth-provider'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: vi.fn() }),
  usePathname: () => '/home',
}))

vi.mock('@/lib/api', () => ({
  getSessionUserWithRefresh: vi.fn(),
}))

afterEach(cleanup)

function TestConsumer() {
  const auth = useAuth()
  return (
    <div>
      <span data-testid="loading">{String(auth.loading)}</span>
      <span data-testid="user">{auth.user?.name ?? 'null'}</span>
    </div>
  )
}

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading initially then resolves', async () => {
    const { getSessionUserWithRefresh } = await import('@/lib/api')
    ;(getSessionUserWithRefresh as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 1,
      name: 'Test User',
      username: 'testuser',
    })

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    )

    expect(screen.getByTestId('loading').textContent).toBe('true')

    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
    })
    expect(screen.getByTestId('user').textContent).toBe('Test User')
  })

  it('sets user to null when unauthenticated', async () => {
    const { getSessionUserWithRefresh } = await import('@/lib/api')
    ;(getSessionUserWithRefresh as ReturnType<typeof vi.fn>).mockResolvedValue(null)

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
    })
    expect(screen.getByTestId('user').textContent).toBe('null')
  })

  it('throws error when useAuth is used outside provider', () => {
    const origConsoleError = console.error
    console.error = vi.fn()

    expect(() => render(<TestConsumer />)).toThrow('useAuth must be used within AuthProvider.')

    console.error = origConsoleError
  })
})
