import { describe, it, expect, vi, beforeEach } from 'vitest'

import { render, screen, fireEvent, waitFor } from '@testing-library/react'

import { LanguageProvider } from '../contexts/LanguageContext'

import { mockUseMeeting, mockUseWebSocket } from './mocks'



vi.mock('../hooks', () => ({

  useMeeting: () => mockUseMeeting(),

  useWebSocket: () => mockUseWebSocket(),

}))



vi.mock('../components/NewMeetingDialog', () => ({

  default: () => <div data-testid="new-meeting-dialog">NewMeetingDialog</div>,

}))



vi.mock('../components/TemplateManagerDialog', () => ({

  default: () => <div data-testid="template-manager-dialog">TemplateManagerDialog</div>,

}))



vi.mock('../components/ExportDialog', () => ({

  default: () => <div data-testid="export-dialog">ExportDialog</div>,

}))



vi.mock('../components/DrawingBoard', () => ({

  default: () => <div data-testid="drawing-board">DrawingBoard</div>,

}))



vi.mock('../components/KanbanBoard', () => ({

  default: () => <div data-testid="kanban-board">KanbanBoard</div>,

}))



const mockAgents = [

  { id: 'iris', name: 'iris', emoji: '馃', title: 'AI Assistant', status: 'idle' as const, current_task: '', message_count: 0 },

  { id: 'codey', name: 'Codey', emoji: '馃捇', title: 'Code Agent', status: 'idle' as const, current_task: '', message_count: 0 },

]



function renderWithProviders(component: React.ReactElement) {

  return render(<LanguageProvider>{component}</LanguageProvider>)

}



describe('MeetingView', () => {

  beforeEach(() => {

    vi.clearAllMocks()

  })



  it('renders meeting sidebar', async () => {

    const MeetingView = (await import('../components/MeetingView')).default

    renderWithProviders(<MeetingView agents={mockAgents} />)



    expect(screen.getByText('馃彌锔?Meeting')).toBeInTheDocument()

  })



  it('shows new meeting button', async () => {

    const MeetingView = (await import('../components/MeetingView')).default

    renderWithProviders(<MeetingView agents={mockAgents} />)



    expect(screen.getByText('+ Start New Meeting')).toBeInTheDocument()

  })



  it('displays meeting room list', async () => {

    const MeetingView = (await import('../components/MeetingView')).default

    renderWithProviders(<MeetingView agents={mockAgents} />)



    expect(screen.getByText('Test Meeting')).toBeInTheDocument()

  })



  it('shows stats in sidebar footer', async () => {

    const MeetingView = (await import('../components/MeetingView')).default

    renderWithProviders(<MeetingView agents={mockAgents} />)



    expect(screen.getByText(/Total:/)).toBeInTheDocument()

    expect(screen.getByText(/Completed:/)).toBeInTheDocument()

  })



  it('shows empty state when no meeting selected', async () => {

    const MeetingView = (await import('../components/MeetingView')).default

    renderWithProviders(<MeetingView agents={mockAgents} />)



    expect(screen.getByText('Select a meeting', { selector: '.empty-text' })).toBeInTheDocument()

  })



  it('opens new meeting dialog on button click', async () => {

    const MeetingView = (await import('../components/MeetingView')).default

    renderWithProviders(<MeetingView agents={mockAgents} />)



    fireEvent.click(screen.getByText('+ Start New Meeting'))

    await waitFor(() => {

      expect(screen.getByTestId('new-meeting-dialog')).toBeInTheDocument()

    })

  })

})

