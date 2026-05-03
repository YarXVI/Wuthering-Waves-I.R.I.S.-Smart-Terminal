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

// Shared TypeScript types

export interface AgentInfo {
  id: string
  name: string
  emoji: string
  title: string
  status: 'idle' | 'thinking' | 'working' | 'error'
  current_task: string
  message_count: number
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  agentId: string
  agentName: string
  timestamp: number
  thinkingContent?: string
}

export interface MeetingRoom {
  room_id: string
  topic?: string
  round_count?: number
  status?: string
  consensus?: boolean
  entry_count?: number
}

export interface WhiteboardEntry {
  entry_id: string
  author: string
  type: string
  content: string
  timestamp: number
  thinking_content?: string
  resolved?: boolean
  assigned_to?: string
  tags?: string[]
}

export interface MeetingSummary {
  topic: string
  participants: string[]
  decisions: string[]
  action_items: string[]
  summary: string
}

export interface MeetingStats {
  total_meetings: number
  completed: number
  consensus_reached: number
  total_rounds: number
}

export interface MeetingTemplate {
  id: string
  name: string
  description: string
  suggested_agents: string[]
  default_rounds: number
}

export type WsStatus = 'connected' | 'reconnecting' | 'disconnected'

// Window agentAPI type
interface AgentAPI {
  health: () => Promise<{ status: string; model: string }>
  listAgents: () => Promise<{ agents: AgentInfo[] }>
  chat: (message: string, agentId: string) => Promise<ChatResponse>
  getMemRAGStatus: () => Promise<{ enabled: boolean }>
  toggleMemRAG: (enabled: boolean) => Promise<void>
  reset: (agentId: string) => Promise<void>
  resetAll: () => Promise<void>
  newSession: (agentId: string) => Promise<void>
  listSessions: (agentId?: string) => Promise<{ sessions: any[] }>
  getSession: (sessionId: string) => Promise<{ messages: any[] }>
  getSettings: () => Promise<any>
  listTemplates: () => Promise<{ templates: any[] }>
  listMeetings: () => Promise<{ meetings: any[] }>
  getMeeting: (roomId: string) => Promise<any>
  startMeetingV2: (topic: string, agents: string[]) => Promise<{ room_id: string }>
  autoDiscuss: (roomId: string) => Promise<any>
  judgeMeetingConsensus: (roomId: string) => Promise<{ consensus: boolean }>
  summarizeMeeting: (roomId: string) => Promise<any>
  deleteMeeting: (roomId: string) => Promise<void>
  addWhiteboardEntry: (roomId: string, type: string, content: string) => Promise<void>
  getWhiteboard: (roomId: string) => Promise<{ entries: any[] }>
  getWhiteboardStats: (roomId: string) => Promise<any>
  listWhiteboardRooms: () => Promise<{ rooms: any[] }>
  searchMeetings: (query: string) => Promise<{ meetings: any[] }>
  getMeetingStats: () => Promise<{ total_meetings: number; completed: number; consensus_reached: number; total_rounds: number }>
  createTemplate: (name: string, description: string, agents: string[], rounds: number) => Promise<any>
  updateTemplate: (templateId: string, name: string, description: string, agents: string[], rounds: number) => Promise<any>
  deleteTemplate: (templateId: string) => Promise<void>
}

declare global {
  interface Window {
    agentAPI: AgentAPI
  }
}

// Agent API Response Types
export interface ChatResponse {
  reply: string
  agent_id: string
  agent_name: string
}

export interface MeetingCreateResponse {
  room_id: string
  topic: string
}
