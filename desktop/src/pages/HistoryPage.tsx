import React, { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

interface SessionInfo {
  agent_id: string
  message_count: number
  created_at: string
  updated_at: string
}

interface ArchivedSession extends SessionInfo {
  archived_at: string
}

const HistoryPage: React.FC = () => {
  const { t } = useLanguage()
  const [sessions, setSessions] = useState<SessionInfo[]>([])
  const [archivedByAgent, setArchivedByAgent] = useState<Record<string, ArchivedSession[]>>({})
  const [selectedSession, setSelectedSession] = useState<{ agent_id: string; messages: any[] } | null>(null)
  const [loading, setLoading] = useState(false)
  const [searchQ, setSearchQ] = useState('')
  const [activeTab, setActiveTab] = useState<'active' | 'archived'>('active')

  useEffect(() => {
    loadSessions()
  }, [])

  async function loadSessions() {
    setLoading(true)
    try {
      const res = await (window as any).agentAPI.listSessions()
      setSessions(res.sessions || [])
    } catch {} finally {
      setLoading(false)
    }
  }

  async function loadArchived(agentId: string) {
    try {
      const res = await (window as any).agentAPI.listArchivedSessions(agentId)
      setArchivedByAgent(prev => ({ ...prev, [agentId]: res.archived_sessions || [] }))
    } catch {}
  }

  async function viewSession(agentId: string) {
    try {
      const res = await (window as any).agentAPI.getSession(agentId)
      setSelectedSession({ agent_id: agentId, messages: res.messages || [] })
    } catch {}
  }

  function formatTime(ts: string) {
    if (!ts) return ''
    const d = new Date(ts)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  }

  function highlightSearch(text: string, q: string) {
    if (!q.trim()) return text
    const parts = text.split(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'))
    return parts.map((part, i) =>
      part.toLowerCase() === q.toLowerCase() ? <mark key={i} style={{background:'rgba(234,179,8,0.3)',borderRadius:2}}>{part}</mark> : part
    )
  }

  const filteredSessions = sessions.filter(s => {
    if (!searchQ.trim()) return true
    const q = searchQ.toLowerCase()
    return s.agent_id.toLowerCase().includes(q)
  })

  return (
    <div style={{ padding: 16, maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: 18, color: 'var(--nb-text-primary)' }}>{t.history.title}</h2>
        <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--nb-text-muted)' }}>
          {t.history.description}
        </p>
      </div>

      {/* Search */}
      <div style={{ marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
        <input
          type="text"
          placeholder={t.history.searchPlaceholder}
          value={searchQ}
          onChange={e => setSearchQ(e.target.value)}
          style={{
            flex: 1, maxWidth: 300,
            background: 'var(--nb-bg-secondary)', border: '1px solid var(--nb-border-strong)',
            borderRadius: 6, color: 'var(--nb-text-primary)', fontSize: 13, padding: '6px 10px',
            outline: 'none', fontFamily: 'inherit'
          }}
        />
        <button
          onClick={() => {
            const data = filteredSessions.map(s => ({
              agent_id: s.agent_id,
              message_count: s.message_count,
              created_at: s.created_at,
              updated_at: s.updated_at
            }))
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `sessions-${new Date().toISOString().slice(0,10)}.json`
            a.click()
            URL.revokeObjectURL(url)
          }}
          style={{
            padding: '6px 12px', borderRadius: 6, fontSize: 12,
            background: 'transparent', color: 'var(--nb-text-muted)',
            border: '1px solid var(--nb-border-strong)', cursor: 'pointer'
          }}
        >{t.history.export}</button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button
          onClick={() => setActiveTab('active')}
          style={{
            padding: '6px 16px', borderRadius: 6, fontSize: 12,
            background: activeTab === 'active' ? 'var(--nb-bg-tertiary)' : 'transparent',
            color: activeTab === 'active' ? 'var(--nb-text-primary)' : 'var(--nb-text-muted)',
            border: '1px solid var(--nb-border-strong)', cursor: 'pointer'
          }}
        >{t.history.activeSessions} ({filteredSessions.length})</button>
        <button
          onClick={() => setActiveTab('archived')}
          style={{
            padding: '6px 16px', borderRadius: 6, fontSize: 12,
            background: activeTab === 'archived' ? 'var(--nb-bg-tertiary)' : 'transparent',
            color: activeTab === 'archived' ? 'var(--nb-text-primary)' : 'var(--nb-text-muted)',
            border: '1px solid var(--nb-border-strong)', cursor: 'pointer'
          }}
        >{t.history.archived}</button>
      </div>

      {/* Content */}
      {loading ? (
        <div style={{ color: 'var(--nb-text-muted)', fontSize: 13 }}>{t.common.loading}</div>
      ) : activeTab === 'active' ? (
        <div style={{
          background: 'var(--nb-bg-secondary)', border: '1px solid var(--nb-border)',
          borderRadius: 8, overflow: 'hidden'
        }}>
          {filteredSessions.length === 0 ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--nb-text-muted)', fontSize: 13 }}>
              {t.history.noActiveSessions}
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{ background: 'var(--nb-bg-primary)', borderBottom: '1px solid var(--nb-border)' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--nb-text-muted)', fontWeight: 500 }}>{t.history.agent}</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--nb-text-muted)', fontWeight: 500 }}>{t.history.messages}</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--nb-text-muted)', fontWeight: 500 }}>{t.history.updated}</th>
                  <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--nb-text-muted)', fontWeight: 500 }}>{t.history.actions}</th>
                </tr>
              </thead>
              <tbody>
                {filteredSessions.map(s => (
                  <tr key={s.agent_id} style={{ borderBottom: '1px solid var(--nb-border)' }}>
                    <td style={{ padding: '8px 12px', color: 'var(--nb-text-primary)' }}>{highlightSearch(s.agent_id, searchQ)}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{s.message_count}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatTime(s.updated_at)}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <button
                        onClick={() => viewSession(s.agent_id)}
                        style={{
                          padding: '3px 10px', borderRadius: 4, fontSize: 11,
                          background: 'transparent', color: 'var(--nb-text-muted)',
                          border: '1px solid var(--nb-border-strong)', cursor: 'pointer'
                        }}
                      >{t.history.view}</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        <div style={{
          background: 'var(--nb-bg-secondary)', border: '1px solid var(--nb-border)',
          borderRadius: 8, padding: 16
        }}>
          <div style={{ fontSize: 12, color: 'var(--nb-text-muted)', marginBottom: 12 }}>
            {t.history.selectAgent}
          </div>
          {Object.keys(archivedByAgent).length === 0 && sessions.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {sessions.map(s => (
                <button key={s.agent_id} onClick={() => loadArchived(s.agent_id)} style={{
                  padding: '4px 12px', borderRadius: 6, fontSize: 11,
                  background: 'var(--nb-bg-primary)', color: 'var(--nb-text-primary)',
                  border: '1px solid var(--nb-border-strong)', cursor: 'pointer'
                }}>{s.agent_id}</button>
              ))}
            </div>
          )}
          {Object.entries(archivedByAgent).map(([agentId, archives]) => (
            <div key={agentId} style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--nb-text-primary)', marginBottom: 8 }}>{agentId}</div>
              {archives.length === 0 ? (
                <div style={{ fontSize: 11, color: 'var(--nb-text-muted)' }}>No archived sessions</div>
              ) : (
                archives.map((a, i) => (
                  <div key={i} style={{
                    padding: '6px 10px', marginBottom: 4,
                    background: 'var(--nb-bg-primary)', borderRadius: 4, fontSize: 11
                  }}>
                    <span style={{ color: 'var(--nb-text-primary)' }}>{a.message_count} msgs</span>
                    <span style={{ color: 'var(--nb-text-muted)', marginLeft: 8 }}>{formatTime(a.archived_at)}</span>
                  </div>
                ))
              )}
            </div>
          ))}
        </div>
      )}

      {/* Session Detail Modal */}
      {selectedSession && (
        <div
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, padding: 16
          }}
          onMouseDown={e => { if (e.target === e.currentTarget) setSelectedSession(null) }}
        >
          <div style={{
            background: 'var(--nb-bg-primary)', border: '1px solid var(--nb-border)',
            borderRadius: 8, width: '100%', maxWidth: 700, maxHeight: '80vh',
            display: 'flex', flexDirection: 'column'
          }}>
            <div style={{
              padding: '12px 16px', borderBottom: '1px solid var(--nb-border)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
              <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--nb-text-primary)' }}>
                {selectedSession.agent_id} â€?{selectedSession.messages.length} messages
              </span>
              <button
                onClick={() => setSelectedSession(null)}
                style={{
                  width: 24, height: 24, fontSize: 14,
                  background: 'transparent', border: '1px solid var(--nb-border-strong)',
                  borderRadius: 4, color: 'var(--nb-text-muted)', cursor: 'pointer'
                }}
              >Ã—</button>
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
              {selectedSession.messages.length === 0 ? (
                <div style={{ color: 'var(--nb-text-muted)', fontSize: 13 }}>No messages</div>
              ) : (
                selectedSession.messages.map((msg: any, i: number) => (
                  <div key={i} style={{ marginBottom: 12 }}>
                    <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                      <span style={{
                        fontSize: 10, padding: '2px 6px', borderRadius: 3,
                        background: msg.role === 'user' ? 'rgba(59,130,246,0.2)' :
                                   msg.role === 'assistant' ? 'rgba(16,185,129,0.2)' :
                                   'rgba(139,92,246,0.2)',
                        color: msg.role === 'user' ? '#3b82f6' :
                               msg.role === 'assistant' ? '#10b981' : '#8b5cf6'
                      }}>{msg.role}</span>
                      {msg.name && <span style={{ fontSize: 10, color: 'var(--nb-text-muted)' }}>{msg.name}</span>}
                    </div>
                    <div style={{
                      background: 'var(--nb-bg-secondary)', borderRadius: 6, padding: '8px 12px',
                      fontSize: 12, color: 'var(--nb-text-primary)', lineHeight: 1.5,
                      whiteSpace: 'pre-wrap', wordBreak: 'break-word'
                    }}>
                      {typeof msg.content === 'string' ? msg.content :
                       JSON.stringify(msg.content, null, 2)}
                    </div>
                    {msg.tool_calls && msg.tool_calls.length > 0 && (
                      <div style={{ marginTop: 4, fontSize: 10, color: 'var(--nb-text-muted)' }}>
                        [{msg.tool_calls.length} tool_call(s)]
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default HistoryPage