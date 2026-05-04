// I.R.I.S. Smart Terminal
// Copyright (C) 2024 I.R.I.S. Agent
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public
// License along with this program.  If not, see
// <https://www.gnu.org/licenses/>.

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
    expect(screen.queryByText(/^馃/)).not.toBeInTheDocument()
  })
})