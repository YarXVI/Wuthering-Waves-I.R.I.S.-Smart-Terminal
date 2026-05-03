import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ThinkingProcess from '../components/ThinkingProcess'

describe('ThinkingProcess', () => {
  const mockContent = 'This is my thinking process:\n1. First step\n2. Second step\n3. Conclusion'

  it('renders thinking content correctly', () => {
    render(<ThinkingProcess content={mockContent} />)
    expect(screen.getByText(/Thinking Process/)).toBeInTheDocument()
  })

  it('contains the thinking content text', () => {
    render(<ThinkingProcess content={mockContent} />)
    expect(screen.getByText(/This is my thinking process/)).toBeInTheDocument()
  })

  it('displays author when provided', () => {
    render(<ThinkingProcess content={mockContent} author="iris" />)
    expect(screen.getByText(/iris/)).toBeInTheDocument()
  })

  it('renders without author', () => {
    render(<ThinkingProcess content={mockContent} />)
    expect(screen.queryByText(/^🧠/)).not.toBeInTheDocument()
  })
})