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