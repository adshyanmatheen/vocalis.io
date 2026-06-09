import { describe, expect, it } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Input } from '@/components/ui/input'

describe('Input', () => {
  it('renders with placeholder', () => {
    render(<Input placeholder="Enter text" />)
    expect(screen.getByPlaceholderText('Enter text')).toBeDefined()
  })

  it('accepts text input via fireEvent', () => {
    render(<Input placeholder="Name" />)
    const input = screen.getByPlaceholderText('Name') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'Matilda' } })
    expect(input.value).toBe('Matilda')
  })

  it('applies data-slot attribute', () => {
    render(<Input placeholder="test" />)
    const input = screen.getByPlaceholderText('test')
    expect(input.getAttribute('data-slot')).toBe('input')
  })

  it('renders as disabled', () => {
    render(<Input disabled placeholder="Disabled" />)
    const input = screen.getByPlaceholderText('Disabled') as HTMLInputElement
    expect(input.disabled).toBe(true)
  })
})
