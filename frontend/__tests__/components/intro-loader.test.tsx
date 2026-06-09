import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import IntroLoader from '@/components/intro-loader'

beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  vi.useRealTimers()
})

describe('IntroLoader', () => {
  it('shows SiteLoader initially', () => {
    render(
      <IntroLoader>
        <div>App Content</div>
      </IntroLoader>,
    )
    expect(screen.queryByText('App Content')).toBeNull()
  })

  it('shows children after timeout', () => {
    render(
      <IntroLoader>
        <div>App Content</div>
      </IntroLoader>,
    )

    act(() => {
      vi.advanceTimersByTime(2000)
    })

    expect(screen.getByText('App Content')).toBeDefined()
  })

  it('cleans up timeout on unmount', () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout')
    const { unmount } = render(
      <IntroLoader>
        <div>Content</div>
      </IntroLoader>,
    )

    unmount()
    expect(clearTimeoutSpy).toHaveBeenCalled()
  })
})
