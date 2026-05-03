import { vi } from 'vitest'

export const mockUseMeeting = () => ({
  rooms: [
    { room_id: 'room-1', topic: 'Test Meeting', status: 'discussing', consensus: false, round_count: 3, entry_count: 5 }
  ],
  activeId: null,
  setActiveId: vi.fn(),
  stats: { total_meetings: 1, completed: 0, consensus_reached: 0, total_rounds: 3 },
  templates: [{ id: 'tpl-1', name: 'Test Template', description: '', suggested_agents: [], default_rounds: 6 }],
  loading: false,
  error: null,
  loadRooms: vi.fn(),
  loadStats: vi.fn(),
  loadTemplates: vi.fn(),
  startMeeting: vi.fn().mockResolvedValue({ room_id: 'new-room' }),
  deleteMeeting: vi.fn().mockResolvedValue(true),
  startDiscuss: vi.fn().mockResolvedValue({ current_round: 1 }),
  judgeConsensus: vi.fn().mockResolvedValue({ consensus: false }),
  summarizeMeeting: vi.fn().mockResolvedValue({ topic: 'Test', participants: [], decisions: [], action_items: [], summary: '' }),
  addWhiteboardEntry: vi.fn(),
  getWhiteboard: vi.fn().mockResolvedValue({ entries: [] }),
  getWhiteboardStats: vi.fn().mockResolvedValue({ total: 5, issues: 1, tasks: 2, notes: 2 }),
  createTemplate: vi.fn(),
  updateTemplate: vi.fn(),
  deleteTemplate: vi.fn(),
  searchMeetings: vi.fn().mockResolvedValue({ meetings: [] }),
  listWhiteboardRooms: vi.fn().mockResolvedValue({ rooms: [] }),
})

export const mockUseWebSocket = () => ({
  status: 'connected' as const,
  sendMessage: vi.fn(),
  lastMessage: null,
})