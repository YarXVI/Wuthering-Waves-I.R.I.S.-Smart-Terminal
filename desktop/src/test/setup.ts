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
import '@testing-library/jest-dom'

window.agentAPI = {
  listAgents: async () => ({ agents: [] }),
  listSessions: async () => ({ sessions: [] }),
  getSession: async () => ({ messages: [] }),
  chat: async () => ({ reply: 'test reply', agent_id: 'iris', agent_name: 'iris' }),
  health: async () => ({ status: 'ok', model: 'test' }),
  getMemRAGStatus: async () => ({ enabled: false }),
  toggleMemRAG: async () => { /* void */ },
  reset: async () => { /* void */ },
  resetAll: async () => { /* void */ },
  newSession: async () => { /* void */ },
  getSettings: async () => ({}),
  listTemplates: async () => ({ templates: [] }),
  listMeetings: async () => ({ meetings: [] }),
  getMeeting: async () => null,
  startMeetingV2: async () => ({ room_id: 'test-room' }),
  autoDiscuss: async () => ({ current_round: 1 }),
  judgeMeetingConsensus: async () => ({ consensus: false }),
  summarizeMeeting: async () => null,
  deleteMeeting: async () => { /* void */ },
  addWhiteboardEntry: async () => { /* void */ },
  getWhiteboard: async () => ({ entries: [] }),
  getWhiteboardStats: async () => null,
  listWhiteboardRooms: async () => ({ rooms: [] }),
  searchMeetings: async () => ({ meetings: [] }),
  getMeetingStats: async () => ({ total_meetings: 0, completed: 0, consensus_reached: 0, total_rounds: 0 }),
  createTemplate: async () => ({}),
  updateTemplate: async () => ({}),
  deleteTemplate: async () => { /* void */ },
}

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})