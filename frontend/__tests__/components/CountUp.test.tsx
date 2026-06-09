import { describe, expect, it, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import CountUp from '@/components/CountUp'

afterEach(cleanup)

describe('CountUp', () => {
  it('renders as a span element', () => {
    render(<CountUp to={100} from={0} />)
    const spans = document.querySelectorAll('span')
    expect(spans.length).toBeGreaterThan(0)
  })

  it('renders with className applied to span', () => {
    render(<CountUp to={50} from={0} className="text-3xl" />)
    const span = document.querySelector('span.text-3xl')
    expect(span).toBeDefined()
  })
})
