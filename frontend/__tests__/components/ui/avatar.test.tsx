import { describe, expect, it, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

afterEach(cleanup)

describe('Avatar', () => {
  it('renders fallback when no image', () => {
    render(
      <Avatar>
        <AvatarFallback>V</AvatarFallback>
      </Avatar>,
    )
    expect(screen.getByText('V')).toBeDefined()
  })

  it('applies data-slot attributes', () => {
    render(
      <Avatar>
        <AvatarFallback>V</AvatarFallback>
      </Avatar>,
    )
    const fallback = screen.getByText('V')
    expect(fallback.getAttribute('data-slot')).toBe('avatar-fallback')
  })

  it('renders image when src provided', () => {
    render(
      <Avatar>
        <AvatarImage src="/test.jpg" alt="Test" />
        <AvatarFallback>V</AvatarFallback>
      </Avatar>,
    )
    const img = document.querySelector("[data-slot='avatar-image']")
    expect(img).toBeDefined()
  })
})
