import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBanner, LoadingOverlay, EmptyState } from '../components/FeedbackComponents'

describe('ErrorBanner', () => {
  it('renders error message', () => {
    render(<ErrorBanner message="Something went wrong" />)
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument()
  })

  it('does not render when message is null', () => {
    render(<ErrorBanner message={null} />)
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('calls onDismiss when dismiss button is clicked', () => {
    const onDismiss = vi.fn()
    render(<ErrorBanner message="Error" onDismiss={onDismiss} />)
    fireEvent.click(screen.getByText('鉁?))
    expect(onDismiss).toHaveBeenCalled()
  })
})

describe('LoadingOverlay', () => {
  it('renders with default message', () => {
    render(<LoadingOverlay />)
    expect(screen.getByText(/Loading/)).toBeInTheDocument()
  })

  it('renders with custom message', () => {
    render(<LoadingOverlay message="Please wait..." />)
    expect(screen.getByText(/Please wait/)).toBeInTheDocument()
  })

  it('renders without message', () => {
    render(<LoadingOverlay message="" />)
    expect(screen.queryByText(/Loading/)).not.toBeInTheDocument()
  })
})

describe('EmptyState', () => {
  it('renders title and icon', () => {
    render(<EmptyState icon="馃摥" title="No items" />)
    expect(screen.getByText(/No items/)).toBeInTheDocument()
    expect(screen.getByText(/馃摥/)).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(<EmptyState title="Empty" description="Nothing here yet" />)
    expect(screen.getByText(/Nothing here yet/)).toBeInTheDocument()
  })

  it('renders action button when provided', () => {
    const onAction = vi.fn()
    render(<EmptyState title="Empty" action={{ label: 'Add Item', onClick: onAction }} />)
    const button = screen.getByText(/Add Item/)
    expect(button).toBeInTheDocument()
    fireEvent.click(button)
    expect(onAction).toHaveBeenCalled()
  })

  it('does not render action when not provided', () => {
    render(<EmptyState title="Empty" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})