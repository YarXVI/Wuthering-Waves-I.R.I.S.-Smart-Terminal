import React, { useState, useEffect } from 'react'
import { useLanguage } from './contexts/LanguageContext'

// ---- Types ----

interface AgentInfo {
  id: string
  name: string
  emoji: string
  title: string
  specialty: string
  status: string
  is_builtin: boolean
}

interface AgentFormData {
  name: string
  title: string
  specialty: string
  emoji: string
  system_prompt: string
}

// ---- Props ----

interface AgentManagerProps {}

const DEFAULT_EMOJIS = ['🤖', '💻', '📝', '🎨', '🔧', '📊', '🎬', '📷', '🎵', '🧪']

// ---- Component ----

const AgentManager: React.FC<AgentManagerProps> = () => {
  const { t } = useLanguage()
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState('')
  const [formData, setFormData] = useState<AgentFormData>({
    name: '',
    title: '',
    specialty: '',
    emoji: '',
    system_prompt: '',
  })

  useEffect(() => {
    loadAgents()
  }, [])

  async function loadAgents() {
    setLoading(true)
    try {
      if (!(window as any).agentAPI) {
        throw new Error(t.settings.agentAPINotAvailable)
      }
      const res = await (window as any).agentAPI.listAgents()
      setAgents(res.agents || [])
    } catch (e: any) {
      setError(e.message || t.settings.loadAgentsFailed)
    } finally {
      setLoading(false)
    }
  }

  function openCreateForm() {
    setEditingId('')
    setFormData({ name: '', title: '', specialty: '', emoji: '', system_prompt: '' })
    setShowForm(true)
  }

  function openEditForm(agent: AgentInfo) {
    setEditingId(agent.id)
    setFormData({
      name: agent.name,
      title: agent.title,
      specialty: agent.specialty,
      emoji: agent.emoji,
      system_prompt: '',
    })
    setShowForm(true)
  }

  function closeForm() {
    setShowForm(false)
    setEditingId('')
    setError('')
  }

  async function handleSubmit() {
    if (!formData.name.trim()) {
      setError(t.settings.agentNameRequired)
      return
    }

    try {
      if (editingId) {
        // Update existing
        const payload: any = { name: formData.name }
        if (formData.title) payload.title = formData.title
        if (formData.specialty) payload.specialty = formData.specialty
        if (formData.emoji) payload.emoji = formData.emoji
        if (formData.system_prompt) payload.system_prompt = formData.system_prompt
        await (window as any).agentAPI.updateAgent(editingId, payload)
      } else {
        // Create new
        await (window as any).agentAPI.createAgent({
          name: formData.name,
          title: formData.title || undefined,
          specialty: formData.specialty || undefined,
          emoji: formData.emoji || undefined,
          system_prompt: formData.system_prompt || undefined,
        })
      }
      closeForm()
      setError('')
      await loadAgents()
    } catch (e: any) {
      setError(e.message || t.settings.operationFailed)
    }
  }

  async function handleDelete(agent: AgentInfo) {
    // 只有爱弥斯不能删�?
    if (agent.id === 'iris') return
    if (!confirm(t.settings.confirmDelete.replace('{name}', agent.name).replace('{id}', agent.id))) return

    try {
      await (window as any).agentAPI.deleteAgent(agent.id)
      await loadAgents()
    } catch (e: any) {
      setError(e.message || t.settings.deleteFailed)
    }
  }

  function getStatusClass(status: string): string {
    switch (status) {
      case 'idle': return 'status-idle'
      case 'thinking': return 'status-thinking'
      case 'working': return 'status-working'
      case 'error': return 'status-error'
      default: return 'status-idle'
    }
  }

  if (loading) {
    return <div className="settings-loading">{t.common.loading}...</div>
  }

  return (
    <div className="agent-manager">
      <div className="agent-manager-header">
        <p className="settings-desc">
          {t.settings.agentsDesc}
        </p>
        <button className="btn-create-agent" onClick={openCreateForm}>
          + {t.settings.createNewAgent}
        </button>
      </div>

      {error && <div className="agent-error">{error}</div>}

      {/* Agent Cards */}
      <div className="agent-grid">
        {agents.map(agent => (
          <div key={agent.id} className={`agent-card ${agent.is_builtin ? 'builtin' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-emoji">{agent.emoji || '🤖'}</span>
              <div className="agent-info">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-title">{agent.title}</span>
              </div>
              <span className={`agent-status ${getStatusClass(agent.status)}`}>
                {agent.status}
              </span>
            </div>

            <div className="agent-id-badge">{agent.id}</div>

            <div className="agent-specialty">
              {agent.specialty || <span className="no-specialty">{t.settings.noSpecialty}</span>}
            </div>

            <div className="agent-card-actions">
              <button className="agent-btn-edit" onClick={() => openEditForm(agent)}>
                {t.settings.edit}
              </button>
              {agent.id === 'iris' ? (
                <span className="builtin-lock" title={t.settings.builtinLock}>🔒</span>
              ) : (
                <button className="agent-btn-delete" onClick={() => handleDelete(agent)}>
                  {t.settings.delete}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create / Edit Form Modal */}
      {showForm && (
        <div className="agent-form-overlay" onClick={closeForm}>
          <div className="agent-form-modal" onClick={e => e.stopPropagation()}>
            <div className="agent-form-header">
              <h3>{editingId ? `${t.settings.editAgent}: ${editingId}` : t.settings.createNewAgent}</h3>
              <button className="settings-close-btn" onClick={closeForm}>�?/button>
            </div>

            <div className="agent-form-body">
              <div className="field-row">
                <label>{t.settings.agentName} *</label>
                <input
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. 剪辑�?
                  disabled={!!editingId}
                />
              </div>

              <div className="field-row">
                <label>{t.settings.agentTitle}</label>
                <input
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. 视频编辑�?
                />
              </div>

              <div className="field-row">
                <label>{t.settings.agentSpecialty}</label>
                <textarea
                  value={formData.specialty}
                  onChange={e => setFormData({ ...formData, specialty: e.target.value })}
                  placeholder="Describe this agent's expertise, e.g. 视频脚本、分镜设计、内容策�?
                  rows={3}
                />
              </div>

              <div className="field-row">
                <label>{t.settings.agentEmoji}</label>
                <div className="emoji-picker">
                  <input
                    value={formData.emoji}
                    onChange={e => setFormData({ ...formData, emoji: e.target.value })}
                    placeholder="e.g. 🎬"
                    maxLength={4}
                    className="emoji-input"
                  />
                  {!editingId && (
                    <div className="emoji-options">
                      {DEFAULT_EMOJIS.map(e => (
                        <span
                          key={e}
                          className={`emoji-option ${formData.emoji === e ? 'selected' : ''}`}
                          onClick={() => setFormData({ ...formData, emoji: e })}
                        >
                          {e}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="field-row">
                <label>{t.settings.agentSystemPrompt} <span className="optional">({t.settings.optional})</span></label>
                <textarea
                  value={formData.system_prompt}
                  onChange={e => setFormData({ ...formData, system_prompt: e.target.value })}
                  placeholder="Leave empty for auto-generated prompt based on name, title and specialty"
                  rows={5}
                />
              </div>
            </div>

            <div className="agent-form-actions">
              {error && <span className="form-error">{error}</span>}
              <button className="agent-btn-cancel" onClick={closeForm}>{t.settings.cancel}</button>
              <button className="agent-btn-save" onClick={handleSubmit}>
                {editingId ? t.settings.saveChanges : t.settings.createNewAgent}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentManager
