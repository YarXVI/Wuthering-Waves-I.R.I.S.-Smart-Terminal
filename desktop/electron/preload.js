const { contextBridge } = require('electron')

const API_BASE = 'http://127.0.0.1:8765'

async function apiFetch(url, options = {}) {
  const res = await fetch(url, options)
  const data = await res.json()
  if (!res.ok) {
    throw new Error(data.detail || `HTTP ${res.status}: ${res.statusText}`)
  }
  return data
}

contextBridge.exposeInMainWorld('agentAPI', {
  // ---- Agents ----
  listAgents: async () => {
    try {
      return await apiFetch(`${API_BASE}/agents`)
    } catch { return { agents: [] } }
  },

  listSessions: async () => {
    try { return await apiFetch(`${API_BASE}/sessions`)
    } catch { return { sessions: [] } }
  },

  getSession: async (agentId) => {
    try { return await apiFetch(`${API_BASE}/agents/${agentId}/session`)
    } catch { return { messages: [] } }
  },

  listArchivedSessions: async (agentId) => {
    try { return await apiFetch(`${API_BASE}/agents/${agentId}/archived-sessions`)
    } catch { return { archived_sessions: [] } }
  },

  getUsageStats: async (days = 7) => {
    try { return await apiFetch(`${API_BASE}/usage/stats?days=${days}`)
    } catch { return { days: [] } }
  },

  getAgent: async (agentId) => {
    try { return await apiFetch(`${API_BASE}/agents/${agentId}`)
    } catch { return null }
  },

  chat: async (message, agentId = 'iris') => {
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

  // ---- System ----
  health: async () => {
    try { return await apiFetch(`${API_BASE}/health`)
    } catch { return { status: 'unreachable' } }
  },

  // ---- MemRAG ----
  getMemRAGStatus: async () => {
    try { return await apiFetch(`${API_BASE}/memrag`)
    } catch { return { enabled: false, embedding_available: false } }
  },

  toggleMemRAG: async (enabled) => {
    return await apiFetch(`${API_BASE}/memrag/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    })
  },

  // ---- Settings ----
  getSettings: async () => {
    return await apiFetch(`${API_BASE}/settings`)
  },

  updateProviders: async (providers) => {
    return await apiFetch(`${API_BASE}/settings/providers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ providers }),
    })
  },

  updateMCPServers: async (servers) => {
    return await apiFetch(`${API_BASE}/settings/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ servers }),
    })
  },

  listSkills: async () => {
    return await apiFetch(`${API_BASE}/skills`)
  },

  toggleSkill: async (name, enabled) => {
    return await apiFetch(`${API_BASE}/skills/${name}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    })
  },

  // ---- 会议�?----
  listWhiteboardRooms: async () => {
    try { return await apiFetch(`${API_BASE}/whiteboard/rooms`)
    } catch { return { rooms: [] } }
  },

  startMeeting: async (topic = '') => {
    return await apiFetch(`${API_BASE}/meetings/start?topic=${encodeURIComponent(topic)}`, { method: 'POST' })
  },

  newSession: async (agentId) => {
    return await apiFetch(`${API_BASE}/agents/${agentId}/new-session`, { method: 'POST' })
  },

  // ---- Custom Agent Management ----
  createAgent: async (data) => {
    return await apiFetch(`${API_BASE}/agents/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
  },

  updateAgent: async (agentId, data) => {
    return await apiFetch(`${API_BASE}/agents/${agentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
  },

  deleteAgent: async (agentId) => {
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

  callAgent: async (agentId, message, callerId = '') => {
    return await apiFetch(`${API_BASE}/collaboration/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, message, caller_id: callerId }),
    })
  },

  getWhiteboard: async (roomId) => {
    try {
      return await apiFetch(`${API_BASE}/whiteboard/${roomId}`)
    } catch { return { entries: [] } }
  },

  addWhiteboardEntry: async (roomId, author, type, content) => {
    return await apiFetch(`${API_BASE}/whiteboard/${roomId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author, type, content }),
    })
  },

  getWhiteboardEvents: async (roomId, count = 20) => {
    try {
      return await apiFetch(`${API_BASE}/whiteboard/${roomId}/events?count=${count}`)
    } catch { return { events: [] } }
  },

  getWhiteboardStats: async (roomId) => {
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

  resolveTask: async (roomId, entryId, resolved = true) => {
    return await apiFetch(`${API_BASE}/whiteboard/${roomId}/${entryId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolved, assigned_to: '' }),
    })
  },

  // ---- 智能会议�?(Phase 2B) ----
  suggestMeetingAgents: async (topic) => {
    try {
      return await apiFetch(`${API_BASE}/meetings/suggest-agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })
    } catch { return { suggested: [], reasoning: '' } }
  },

  startMeetingV2: async (topic, agents = []) => {
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

  getMeeting: async (roomId) => {
    try { return await apiFetch(`${API_BASE}/meetings/${roomId}`)
    } catch { return null }
  },

  runMeetingRound: async (roomId) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/round`, { method: 'POST' })
  },

  autoDiscuss: async (roomId, maxRounds = 20) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/auto-discuss?max_rounds=${maxRounds}`, { method: 'POST' })
  },

  judgeMeetingConsensus: async (roomId) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/judge`, { method: 'POST' })
  },

  summarizeMeeting: async (roomId) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/summarize`, { method: 'POST' })
  },

  createSubMeeting: async (roomId, initiator, issue) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}/sub-meeting?initiator=${encodeURIComponent(initiator)}&issue=${encodeURIComponent(issue)}`, { method: 'POST' })
  },

  // ---- Phase 1: Templates & Search & Stats ----
  listTemplates: async () => {
    try { return await apiFetch(`${API_BASE}/meetings/templates`)
    } catch { return { templates: [] } }
  },

  createTemplate: async (name, description, suggestedAgents, defaultRounds = 6) => {
    return await apiFetch(`${API_BASE}/meetings/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, suggested_agents: suggestedAgents, default_rounds: defaultRounds }),
    })
  },

  updateTemplate: async (templateId, name, description, suggestedAgents, defaultRounds) => {
    return await apiFetch(`${API_BASE}/meetings/templates/${templateId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description, suggested_agents: suggestedAgents, default_rounds: defaultRounds }),
    })
  },

  deleteTemplate: async (templateId) => {
    return await apiFetch(`${API_BASE}/meetings/templates/${templateId}`, {
      method: 'DELETE',
    })
  },

  createFromTemplate: async (templateId, topic, agents = []) => {
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

  advancedSearchMeetings: async (params = {}) => {
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

  deleteMeeting: async (roomId) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}`, {
      method: 'DELETE',
    })
  },

  listWorkflows: async () => {
    try { return await apiFetch(`${API_BASE}/workflows`)
    } catch { return { workflows: [] } }
  },

  getWorkflow: async (workflowId) => {
    try { return await apiFetch(`${API_BASE}/workflows/${workflowId}`)
    } catch { return null }
  },

  saveWorkflow: async (workflow) => {
    return await apiFetch(`${API_BASE}/workflows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workflow),
    })
  },

  deleteWorkflow: async (workflowId) => {
    return await apiFetch(`${API_BASE}/workflows/${workflowId}`, {
      method: 'DELETE',
    })
  },

  executeWorkflow: async (steps = []) => {
    return await apiFetch(`${API_BASE}/workflows/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ steps }),
    })
  },
})
