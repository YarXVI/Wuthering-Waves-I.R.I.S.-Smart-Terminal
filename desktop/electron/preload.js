const { contextBridge } = require('electron')

const API_BASE = 'http://127.0.0.1:8000'

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

  getAgent: async (agentId) => {
    try {
      return await apiFetch(`${API_BASE}/agents/${agentId}`)
    } catch { return null }
  },

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

  // ---- Chat ----
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

  // ---- Health ----
  health: async () => {
    try {
      return await apiFetch(`${API_BASE}/health`)
    } catch { return { status: 'unreachable' } }
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

  // ---- Meetings ----
  listMeetings: async () => {
    try { return await apiFetch(`${API_BASE}/meetings`)
    } catch { return { meetings: [] } }
  },

  startMeeting: async (topic = '') => {
    return await apiFetch(`${API_BASE}/meetings/start?topic=${encodeURIComponent(topic)}`, { method: 'POST' })
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

  deleteMeeting: async (roomId) => {
    return await apiFetch(`${API_BASE}/meetings/${roomId}`, { method: 'DELETE' })
  },

  // ---- Workflows ----
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

  // ---- Whiteboard ----
  listWhiteboardRooms: async () => {
    try { return await apiFetch(`${API_BASE}/whiteboard/rooms`)
    } catch { return { rooms: [] } }
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

  // ---- MemRAG ----
  getMemRAGStatus: async () => {
    try {
      return await apiFetch(`${API_BASE}/memrag`)
    } catch { return { enabled: false, embedding_available: false } }
  },

  toggleMemRAG: async (enabled) => {
    return await apiFetch(`${API_BASE}/memrag/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    })
  },

  // ---- Skills ----
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

  // ---- Collaboration ----
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
})
