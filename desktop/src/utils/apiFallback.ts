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

const API_BASE = 'http://localhost:8000'

async function apiFetch(url: string, options: RequestInit = {}) {
  const res = await fetch(url, options)
  const data = await res.json()
  if (!res.ok) {
    throw new Error(data.detail || `HTTP ${res.status}: ${res.statusText}`)
  }
  return data
}

export const createApiFallback = () => ({
  listAgents: async () => {
    try {
      return await apiFetch(`${API_BASE}/agents`)
    } catch { return { agents: [] } }
  },

  listSessions: async () => {
    try { return await apiFetch(`${API_BASE}/sessions`)
    } catch { return { sessions: [] } }
  },

  getSession: async (agentId: string) => {
    try { return await apiFetch(`${API_BASE}/agents/${agentId}/session`)
    } catch { return { messages: [] } }
  },

  listArchivedSessions: async (agentId: string) => {
    try { return await apiFetch(`${API_BASE}/agents/${agentId}/archived-sessions`)
    } catch { return { archived_sessions: [] } }
  },

  getUsageStats: async (days = 7) => {
    try { return await apiFetch(`${API_BASE}/usage/stats?days=${days}`)
    } catch { return { days: [] } }
  },

  getAgent: async (agentId: string) => {
    try { return await apiFetch(`${API_BASE}/agents/${agentId}`)
    } catch { return null }
  },

  chat: async (message: string, agentId = 'iris') => {
    return await apiFetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, agent_id: agentId }),
    })
  },

  reset: async (agentId = 'iris') => {
    return await apiFetch(`${API_BASE}/reset/${agentId}`, { method: 'POST' })
  },

  resetAll: async () => {
    return await apiFetch(`${API_BASE}/reset`, { method: 'POST' })
  },

  health: async () => {
    try { return await apiFetch(`${API_BASE}/health`)
    } catch { return { status: 'unreachable' } }
  },

  getMemRAGStatus: async () => {
    try { return await apiFetch(`${API_BASE}/memrag`)
    } catch { return { enabled: false, embedding_available: false } }
  },

  toggleMemRAG: async (enabled: boolean) => {
    return await apiFetch(`${API_BASE}/memrag/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    })
  },

  getSettings: async () => {
    return await apiFetch(`${API_BASE}/settings`)
  },

  updateProviders: async (providers: any[]) => {
    return await apiFetch(`${API_BASE}/settings/providers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ providers }),
    })
  },

  updateMCPServers: async (servers: any[]) => {
    return await apiFetch(`${API_BASE}/settings/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ servers }),
    })
  },

  listSkills: async () => {
    return await apiFetch(`${API_BASE}/skills`)
  },

  toggleSkill: async (name: string, enabled: boolean) => {
    return await apiFetch(`${API_BASE}/skills/${name}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    })
  },

  listWhiteboardRooms: async () => {
    try { return await apiFetch(`${API_BASE}/whiteboard/rooms`)
    } catch { return { rooms: [] } }
  },

  startMeeting: async (topic = '') => {
    return await apiFetch(`${API_BASE}/meetings/start?topic=${encodeURIComponent(topic)}`, { method: 'POST' })
  },

  newSession: async (agentId: string) => {
    return await apiFetch(`${API_BASE}/agents/${agentId}/new-session`, { method: 'POST' })
  },

  createAgent: async (data: any) => {
    return await apiFetch(`${API_BASE}/agents/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
  },

  updateAgent: async (agentId: string, data: any) => {
    return await apiFetch(`${API_BASE}/agents/${agentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
  },

  deleteAgent: async (agentId: string) => {
    return await apiFetch(`${API_BASE}/agents/${agentId}`, {
      method: 'DELETE',
    })
  },

  getCollaborationStatus: async () => {
    try {
      return await apiFetch(`${API_BASE}/collaboration/status`)
    } catch { return { agents_count: 0, agents: [] } }
  },

  listCollaborationAgents: async () => {
    try { return await apiFetch(`${API_BASE}/collaboration/agents`)
    } catch { return { agents: [] } }
  },

  callAgent: async (agentId: string, message: string, callerId = '') => {
    return await apiFetch(`${API_BASE}/collaboration/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, message, caller_id: callerId }),
    })
  },

  getWhiteboard: async (roomId: string) => {
    try {
      return await apiFetch(`${API_BASE}/whiteboard/${roomId}`)
    } catch { return { entries: [] } }
  },

  addWhiteboardEntry: async (roomId: string, author: string, type: string, content: any) => {
    return await apiFetch(`${API_BASE}/whiteboard/${roomId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author, type, content }),
    })
  },

  getWhiteboardEvents: async (roomId: string, count = 20) => {
    try {
      return await apiFetch(`${API_BASE}/whiteboard/${roomId}/events?count=${count}`)
    } catch { return { events: [] } }
  },

  getWhiteboardStats: async (roomId: string) => {
    try {
      return await apiFetch(`${API_BASE}/whiteboard/${roomId}/stats`)
    } catch { return null }
  },

  listAllTasks: async (status = '') => {
    try {
      const url = status ? `${API_BASE}/tasks?status=${status}` : `${API_BASE}/tasks`
      return await apiFetch(url)
    } catch { return { tasks: [] } }
  },

  resolveTask: async (roomId: string, entryId: string, resolved = true) => {
    return await apiFetch(`${API_BASE}/whiteboard/${roomId}/${entryId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolved, assigned_to: '' }),
    })
  },

  suggestMeetingAgents: async (topic: string) => {
    try {
      return await apiFetch(`${API_BASE}/meetings/suggest-agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })
    } catch { return { suggested: [], reasoning: '' } }
  },

  startMeetingV2: async (topic: string, agents: string[] = []) => {
    return await apiFetch(`${API_BASE}/meetings/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, agents }),
    })
  },

  listMeetings: async () => {
    try { return await apiFetch(`${API_BASE}/meetings`)
    } catch { return { meetings: [] } }
  },

  getMeeting: async (roomId: string) => {
    try { return await apiFetch(`${API_BASE}/meetings/${roomId}`)
    } catch { return null }
  },

  runMeetingRound: async (roomId: string) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/round`, { method: 'POST' })
  },

  autoDiscuss: async (roomId: string, maxRounds = 20) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/auto-discuss?max_rounds=${maxRounds}`, { method: 'POST' })
  },

  judgeMeetingConsensus: async (roomId: string) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/judge`, { method: 'POST' })
  },

  summarizeMeeting: async (roomId: string) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/summarize`, { method: 'POST' })
  },

  createSubMeeting: async (roomId: string, initiator: string, issue: string) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/sub-meeting?initiator=${encodeURIComponent(initiator)}&issue=${encodeURIComponent(issue)}`, { method: 'POST' })
  },

  listTemplates: async () => {
    try { return await apiFetch(`${API_BASE}/meetings/templates`)
    } catch { return { templates: [] } }
  },

  createTemplate: async (name: string, description: string, suggestedAgents: string[], defaultRounds = 6) => {
    return await apiFetch(`${API_BASE}/meetings/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, suggested_agents: suggestedAgents, default_rounds: defaultRounds }),
    })
  },

  updateTemplate: async (templateId: string, name: string, description: string, suggestedAgents: string[], defaultRounds: number) => {
    return await apiFetch(`${API_BASE}/meetings/templates/${templateId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, suggested_agents: suggestedAgents, default_rounds: defaultRounds }),
    })
  },

  deleteTemplate: async (templateId: string) => {
    return await apiFetch(`${API_BASE}/meetings/templates/${templateId}`, {
      method: 'DELETE',
    })
  },

  createFromTemplate: async (templateId: string, topic: string, agents: string[] = []) => {
    return await apiFetch(`${API_BASE}/meetings/from-template`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ template_id: templateId, topic, agents }),
    })
  },

  searchMeetings: async (query = '') => {
    try { return await apiFetch(`${API_BASE}/meetings/search?q=${encodeURIComponent(query)}`)
    } catch { return { meetings: [] } }
  },

  advancedSearchMeetings: async (params: any = {}) => {
    try {
      return await apiFetch(`${API_BASE}/meetings/advanced-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      })
    } catch { return { meetings: [], total: 0 } }
  },

  getMeetingStats: async () => {
    try { return await apiFetch(`${API_BASE}/meetings/stats`)
    } catch { return { total_meetings: 0, completed: 0, consensus_reached: 0, total_rounds: 0 } }
  },

  deleteMeeting: async (roomId: string) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}`, {
      method: 'DELETE',
    })
  },

  listWorkflows: async () => {
    try { return await apiFetch(`${API_BASE}/workflows`)
    } catch { return { workflows: [] } }
  },

  getWorkflow: async (workflowId: string) => {
    try { return await apiFetch(`${API_BASE}/workflows/${workflowId}`)
    } catch { return null }
  },

  saveWorkflow: async (workflow: any) => {
    return await apiFetch(`${API_BASE}/workflows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workflow),
    })
  },

  deleteWorkflow: async (workflowId: string) => {
    return await apiFetch(`${API_BASE}/workflows/${workflowId}`, {
      method: 'DELETE',
    })
  },

  executeWorkflow: async (steps: any[] = []) => {
    return await apiFetch(`${API_BASE}/workflows/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ steps }),
    })
  },
})

export function initApiFallback() {
  if (!(window as any).agentAPI) {
    console.log('[DEBUG] Electron agentAPI not found, using fallback API')
    ;(window as any).agentAPI = createApiFallback()
  }
}
