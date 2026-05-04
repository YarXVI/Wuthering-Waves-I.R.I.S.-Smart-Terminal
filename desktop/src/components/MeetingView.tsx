import React, { useState, useRef, useEffect } from 'react'

import MarkdownContent from './MarkdownContent'

import DrawingBoard from './DrawingBoard'

import KanbanBoard from './KanbanBoard'

import NewMeetingDialog from './NewMeetingDialog'

import TemplateManagerDialog from './TemplateManagerDialog'

import ExportDialog from './ExportDialog'

import ThinkingProcess from './ThinkingProcess'

import { useMeeting, useWebSocket } from '../hooks'

import { useLanguage } from '../contexts/LanguageContext'



interface AgentInfo {

  id: string; name: string; emoji: string; title: string; specialty?: string

}



interface WhiteboardEntry {

  entry_id: string; author: string; type: string; content: string; timestamp: number; thinking_content?: string

}



interface MeetingSummary {

  topic: string; participants: string[]; decisions: string[]; action_items: string[]; summary: string

}



interface MeetingViewProps {

  agents: AgentInfo[]

}



const API = window as any



function formatTime(ts: number): string {

  const d = new Date(ts * 1000)

  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`

}



const MeetingView: React.FC<MeetingViewProps> = ({ agents }) => {

  const { t } = useLanguage()

  const {

    rooms,

    activeId,

    setActiveId,

    stats,

    templates,

    loadRooms,

    loadStats,

    loadTemplates,

    startMeeting,

    deleteMeeting,

    startDiscuss: startDiscussHook,

    judgeConsensus,

    summarizeMeeting,

    addWhiteboardEntry,

    getWhiteboard,

    getWhiteboardStats,

    createTemplate,

    updateTemplate,

    deleteTemplate,

  } = useMeeting()



  const [entries, setEntries] = useState<WhiteboardEntry[]>([])

  const [running, setRunning] = useState(false)

  const [consensus, setConsensus] = useState(false)

  const [rounds, setRounds] = useState(0)

  const [summary, setSummary] = useState<MeetingSummary | null>(null)

  const [summarizing, setSummarizing] = useState(false)

  const [wbStats, setWbStats] = useState<any>(null)

  const [searchQ, setSearchQ] = useState('')

  const [activeTpl, setActiveTpl] = useState('')



  const [showNewMeetingDlg, setShowNewMeetingDlg] = useState(false)

  const [showTplDlg, setShowTplDlg] = useState(false)

  const [showExportDlg, setShowExportDlg] = useState(false)

  const [exportMd, setExportMd] = useState('')

  const [showDrawDlg, setShowDrawDlg] = useState(false)

  const [showKanbanDlg, setShowKanbanDlg] = useState(false)



  const feedRef = useRef<HTMLDivElement>(null)



  // WebSocket setup

  const wsUrl = activeId ? `ws://127.0.0.1:8000/ws/${activeId}` : null

  const { status: wsStatus, send } = useWebSocket({

    url: wsUrl,

    debugName: 'MeetingView',

    maxReconnectAttempts: 3,

    onMessage: (msg) => handleWsMessage(msg),

  })



  const handleWsMessage = (msg: any) => {

    switch (msg.type) {

      case 'entry_added':

        setEntries(prev => [...prev, msg.entry])

        break

      case 'round_added':

        if (msg.current_round) setRounds(msg.current_round)

        if (msg.round?.content) {

          setEntries(prev => [...prev, {

            entry_id: `round_${msg.round.round_number}`,

            author: msg.round.author,

            type: msg.round.type || 'discussion',

            content: msg.round.content,

            timestamp: msg.round.timestamp || Date.now() / 1000,

          }])

        }

        break

      case 'auto_discuss_complete':

        setRounds(msg.rounds_completed || 0)

        setConsensus(msg.consensus || false)

        if (activeId) loadEntries(activeId)

        loadRooms()

        break

      case 'judge_result':

        setConsensus(msg.consensus || false)

        if (activeId) loadEntries(activeId)

        break

      case 'summary_generated':

        if (activeId) loadEntries(activeId)

        loadRooms()

        break

      case 'meeting_created':

        loadRooms()

        break

    }

  }



  useEffect(() => {

    feedRef.current?.scrollIntoView({ behavior: 'smooth' })

  }, [entries])



  // Poll rooms every 5 seconds

  useEffect(() => {

    const interval = setInterval(() => loadRooms(), 5000)

    return () => clearInterval(interval)

  }, [loadRooms])



  // Load entries when activeId changes

  useEffect(() => {

    if (activeId) {

      loadEntries(activeId)

      loadWbStats(activeId)

    } else {

      setEntries([])

      setSummary(null)

      setConsensus(false)

      setRounds(0)

      setWbStats(null)

    }

  }, [activeId])



  // Filter rooms by template

  const filteredRooms = activeTpl

    ? rooms.filter(r => (r.topic || '').toLowerCase().includes(activeTpl))

    : rooms



  const loadEntries = async (roomId: string) => {

    try {

      const res = await getWhiteboard(roomId)

      if (res.entries) setEntries(res.entries)

      const m = await API.agentAPI.getMeeting(roomId)

      if (m) {

        setConsensus(m.consensus)

        setRounds(m.rounds?.length || 0)

      }

    } catch {}

  }



  const loadWbStats = async (roomId: string) => {

    try {

      const res = await getWhiteboardStats(roomId)

      setWbStats(res)

    } catch {

      setWbStats(null)

    }

  }



  const handleStartMeeting = async (topic: string, selectedAgents: string[]) => {

    setShowNewMeetingDlg(false)

    setRunning(true)

    setSummary(null)

    try {

      const agentList = selectedAgents.length > 0 ? selectedAgents : agents.filter(a => a.id !== 'iris').slice(0, 2).map(a => a.id)

      const created = await startMeeting(topic, agentList)

      if (created) {

        setActiveId(created.room_id)

        await startDiscussHook(created.room_id)

      }

    } catch (e: any) {

      setEntries(prev => [...prev, {

        entry_id: 'error', author: 'system', type: 'note',

        content: `[Error] ${e.message}`, timestamp: Date.now() / 1000,

      }])

    }

    setRunning(false)

    loadRooms()

    loadStats()

  }



  const handleDiscuss = async () => {

    if (!activeId) return

    setRunning(true)

    try {

      const r = await startDiscussHook(activeId)

      if (r?.current_round) setRounds(r.current_round)

    } catch {}

    setRunning(false)

    if (activeId) loadEntries(activeId)

    loadRooms()

    loadStats()

  }



  const handleJudge = async () => {

    if (!activeId) return

    try {

      const r = await judgeConsensus(activeId)

      setConsensus(r?.consensus || false)

      if (activeId) loadEntries(activeId)

      loadRooms()

    } catch {}

  }



  const handleSummary = async () => {

    if (!activeId) return

    setSummarizing(true)

    try {

      const r = await summarizeMeeting(activeId)

      setSummary(r)

      if (activeId) loadEntries(activeId)

    } catch (e: any) {

      setEntries(prev => [...prev, {

        entry_id: 'err', author: 'system', type: 'note',

        content: `[Summary Error] ${e.message}`, timestamp: Date.now() / 1000,

      }])

    }

    setSummarizing(false)

    loadRooms()

    loadStats()

  }



  const handleDelete = async (roomId: string) => {

    if (!confirm(`Delete meeting "${roomId}"? This cannot be undone.`)) return

    try {

      await deleteMeeting(roomId)

    } catch (e: any) {

      alert(`Delete failed: ${e.message}`)

    }

  }



  const handleAddIssue = async () => {

    if (!activeId) return

    const content = prompt('Issue description:')

    if (!content?.trim()) return

    try {

      await addWhiteboardEntry(activeId, 'issue', content.trim())

      if (activeId) loadEntries(activeId)

      loadWbStats(activeId)

    } catch {}

  }



  const handleAddTask = async () => {

    if (!activeId) return

    const content = prompt('Task description:')

    if (!content?.trim()) return

    try {

      await addWhiteboardEntry(activeId, 'task', content.trim())

      if (activeId) loadEntries(activeId)

      loadWbStats(activeId)

    } catch {}

  }



  const openExportDlg = async () => {

    if (!activeId) return

    try {

      const res = await fetch(`http://127.0.0.1:8000/meetings/${activeId}/export`)

      const md = await res.text()

      setExportMd(md)

      setShowExportDlg(true)

    } catch {

      alert('Failed to export meeting')

    }

  }



  const downloadExport = () => {

    const blob = new Blob([exportMd], { type: 'text/markdown' })

    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')

    a.href = url

    a.download = `meeting-${activeId}.md`

    a.click()

    URL.revokeObjectURL(url)

  }



  const copyExport = () => {

    navigator.clipboard.writeText(exportMd)

    alert('Copied to clipboard!')

  }



  const handleCreateTemplate = async (data: { name: string; description: string; suggested_agents: string[]; default_rounds: number }) => {

    try {

      await createTemplate(data.name, data.description, data.suggested_agents, data.default_rounds)

      await loadTemplates()

    } catch {}

  }



  const handleUpdateTemplate = async (id: string, data: { name: string; description: string; suggested_agents: string[]; default_rounds: number }) => {

    try {

      await updateTemplate(id, data.name, data.description, data.suggested_agents, data.default_rounds)

      await loadTemplates()

    } catch {}

  }



  const handleDeleteTemplate = async (tplId: string) => {

    try {

      await deleteTemplate(tplId)

      await loadTemplates()

    } catch {}

  }



  const authorName = (a: string) => {

    return { system: 'System', iris: '🤖 iris', codey: '💻 Codey', scribe: '📝 Scribe' }[a] || a

  }



  const getEmoji = (a: string) => {

    return { system: '📢', iris: '🤖', codey: '💻', scribe: '📝' }[a] || '?'

  }



  const activeRoom = filteredRooms.find(r => r.room_id === activeId)



  return (

    <>

      <div className="sidebar">

        <div className="sidebar-header">

          <span>🏢 {t.meeting.title}</span>

        </div>

        <div className="sidebar-search">

          <input placeholder={t.meeting.topicPlaceholder} value={searchQ} onChange={e => { setSearchQ(e.target.value); loadRooms(e.target.value) }} style={{ width: '100%', padding: '6px 10px', borderRadius: 6, border: '1px solid var(--nb-border-strong)', background: 'var(--nb-bg-tertiary)', color: 'var(--nb-text-primary)', fontSize: 12 }} />

        </div>

        <div className="sidebar-actions" style={{ padding: '8px 12px', display: 'flex', flexDirection: 'column', gap: 6, borderBottom: '1px solid var(--nb-border)' }}>

          <button className="new-meeting-btn" onClick={() => setShowNewMeetingDlg(true)} disabled={running}>

            {running ? `⏳ ${t.meeting.inProgress}` : `+ ${t.meeting.newMeeting}`}

          </button>

          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>

            {templates.slice(0, 4).map(t => (

              <button key={t.id}

                style={{

                  padding: '4px 8px', borderRadius: 6, fontSize: 10, cursor: 'pointer',

                  background: activeTpl === t.id ? 'var(--nb-accent-bg)' : 'transparent',

                  color: activeTpl === t.id ? 'var(--nb-accent-light)' : 'var(--nb-text-muted)',

                  border: activeTpl === t.id ? '1px solid var(--nb-border-accent)' : '1px solid var(--nb-border-strong)',

                  fontFamily: 'inherit'

                }}

                onClick={() => { setActiveTpl(t.id); setTimeout(() => loadRooms(), 0) }}

              >

                {t.name}

              </button>

            ))}

            <button style={{ padding: '4px 8px', borderRadius: 6, fontSize: 10, cursor: 'pointer', background: 'transparent', color: 'var(--nb-text-muted)', border: '1px dashed var(--nb-border-strong)', fontFamily: 'inherit' }}

              onClick={() => setShowTplDlg(true)}>鈿欙笍</button>

          </div>

        </div>

        <div className="room-list">

          {filteredRooms.map(r => (

            <div key={r.room_id}

              className={`room-item ${activeId === r.room_id ? 'active' : ''}`}

              onClick={() => setActiveId(r.room_id)}

            >

              <div className="room-topic">{r.topic || t.meeting.untitled}</div>

              <div className="room-meta">

                {r.consensus ? '✓' : r.status === 'completed' ? '✓' : '⏳'} {r.round_count || 0} {t.meeting.rounds} · {r.entry_count || 0} {t.meeting.entries}

              </div>

              <button className="room-delete" onClick={(e) => { e.stopPropagation(); handleDelete(r.room_id) }}>✗</button>

            </div>

          ))}

        </div>

        {stats && (

          <div style={{ padding: '8px 12px', borderTop: '1px solid var(--nb-border)', fontSize: 10, color: 'var(--nb-text-muted)' }}>

            {t.meeting.total}: {stats.total_meetings} | {t.meeting.completed}: {stats.completed} | {t.meeting.consensusReached}: {stats.consensus_reached}

          </div>

        )}

      </div>



      <div className="chat-area">

        <header className="chat-header">

          <span>

            <div className="chat-agent-title">

              {activeRoom?.topic || t.meeting.meetingRoom}

            </div>

            <div className="chat-agent-title">

              {activeId ? `${rounds > 0 ? `${t.meeting.rounds} ${rounds} 路 ` : ''}${entries.length} ${t.meeting.entries}` : t.meeting.noMeetings}

            </div>

          </span>

          <div className="chat-header-actions">

            {activeId && (

              <button style={{ padding: '3px 8px', borderRadius: 4, fontSize: 11, color: 'var(--nb-text-muted)', border: '1px solid var(--nb-border-strong)', background: 'transparent', cursor: 'pointer' }} onClick={openExportDlg}>

                {t.meeting.export}

              </button>

            )}

            <span className="meeting-status-badge">

              <span className={`meeting-dot ${consensus ? 'done' : running ? 'running' : 'idle'}`} />

              {consensus ? t.meeting.consensus : running ? t.meeting.running : t.meeting.idle}

            </span>

            {activeId && (

              <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, background: wsStatus === 'connected' ? 'rgba(52,211,153,0.2)' : wsStatus === 'reconnecting' ? 'rgba(251,191,36,0.2)' : 'rgba(248,113,113,0.2)', color: wsStatus === 'connected' ? '#34d399' : wsStatus === 'reconnecting' ? '#fbbf24' : '#f87171', border: '1px solid var(--nb-border)' }}>

                {wsStatus === 'connected' ? t.meeting.live : wsStatus === 'reconnecting' ? t.meeting.reconnecting : t.meeting.offline}

              </span>

            )}

          </div>

        </header>



        <div className="messages meeting-feed">

          {!activeId ? (

            <div className="empty-state" style={{ paddingTop: 80 }}>

              <div className="empty-icon">🏢</div>

              <div className="empty-text" style={{ fontSize: 15 }}>{t.meeting.selectMeeting}</div>

            </div>

          ) : (

            <>

              {entries.map((e, i) => (

                <div key={e.entry_id || i} className={`message assistant meeting-msg feed-${e.author}`}>

                  <div className="msg-avatar" style={{

                    background: e.author === 'system' ? 'linear-gradient(135deg, #64748b, #94a3b8)' : e.author === 'iris' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : e.author === 'codey' ? 'linear-gradient(135deg, #10b981, #34d399)' : e.author === 'scribe' ? 'linear-gradient(135deg, #f59e0b, #fbbf24)' : '#6366f1'

                  }}>

                    {getEmoji(e.author)}

                  </div>

                  <div className="msg-body">

                    <div className="msg-meta">

                      <span className="msg-name">{authorName(e.author)}</span>

                      <span className="msg-time">{formatTime(e.timestamp)}</span>

                      <span className="meeting-entry-type">{e.type}</span>

                    </div>

                    {e.thinking_content && (

                      <ThinkingProcess content={e.thinking_content} author={authorName(e.author)} />

                    )}

                    <div className="msg-content"><MarkdownContent content={e.content} /></div>

                  </div>

                </div>

              ))}

              {summary && (

                <div className="message assistant meeting-msg feed-iris" style={{ border: '1px solid var(--nb-border-accent)', borderRadius: 10, padding: 14 }}>

                  <div className="msg-avatar" style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>馃搵</div>

                  <div className="msg-body">

                    <div className="msg-meta"><span className="msg-name" style={{ color: 'var(--nb-accent-light)' }}>{t.meeting.summary}</span></div>

                    <div style={{ fontSize: 13, lineHeight: 1.6 }}>

                      <div><strong>{t.meeting.topic}: </strong>{summary.topic}</div>

                      <div><strong>{t.meeting.participants}: </strong>{summary.participants.join(', ')}</div>

                      <div style={{ marginTop: 8 }}><strong>{t.meeting.decisions}:</strong></div>

                      <ul style={{ paddingLeft: 20, margin: '4px 0' }}>{summary.decisions.map((d, i) => <li key={i} style={{ fontSize: 13 }}>{d}</li>)}</ul>

                      <div><strong>{t.meeting.actionItems}:</strong></div>

                      <ul style={{ paddingLeft: 20, margin: '4px 0' }}>{summary.action_items.map((a, i) => <li key={i} style={{ fontSize: 13 }}>{a}</li>)}</ul>

                    </div>

                  </div>

                </div>

              )}

              <div ref={feedRef} />

            </>

          )}

        </div>



        {activeId && (

          <div className="meeting-actions">

            <button className="meeting-btn" onClick={handleDiscuss} disabled={running}>

              {running ? `⏳ ${t.meeting.running}` : `💬 ${t.meeting.discuss}`}

            </button>

            <button className="meeting-btn" onClick={handleJudge} disabled={running}>

              鈿栵笍 {t.meeting.judge}

            </button>

            <button className="meeting-btn" onClick={handleSummary} disabled={summarizing}>

              {summarizing ? `⏳ ${t.meeting.summarizing}` : `📝 ${t.meeting.summary}`}

            </button>

            <button className="meeting-btn" onClick={() => setShowDrawDlg(true)}>

              📋 {t.meeting.draw}

            </button>

            <button className="meeting-btn" onClick={() => setShowKanbanDlg(true)}>

              📋 {t.meeting.tasks}

            </button>

            <button className="meeting-btn" onClick={handleAddIssue}>

              🔴 {t.meeting.issue}

            </button>

            <button className="meeting-btn" onClick={handleAddTask}>

              ✓ {t.meeting.task}

            </button>

          </div>

        )}

        {wbStats && activeId && (

          <div className="meeting-wb-stats">

            <span>📊 {wbStats.total || 0} {t.meeting.entries}</span>

            <span>🔴 {wbStats.issues || 0} {t.meeting.issue}</span>

            <span>✓ {wbStats.tasks || 0} {t.meeting.task}</span>

            <span>📝 {wbStats.notes || 0} {t.meeting.note}</span>

          </div>

        )}

      </div>



      {showNewMeetingDlg && (

        <div className="dialog-overlay" onMouseDown={e => { if (e.target === e.currentTarget) setShowNewMeetingDlg(false) }}>

          <NewMeetingDialog

            agents={agents}

            templates={templates}

            onClose={() => setShowNewMeetingDlg(false)}

            onStart={handleStartMeeting}

          />

        </div>

      )}



      {showTplDlg && (

        <div className="dialog-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}

          onMouseDown={e => { if (e.target === e.currentTarget) setShowTplDlg(false) }}>

          <TemplateManagerDialog

            templates={templates}

            agents={agents}

            onClose={() => setShowTplDlg(false)}

            onCreate={handleCreateTemplate}

            onUpdate={handleUpdateTemplate}

            onDelete={handleDeleteTemplate}

          />

        </div>

      )}



      {showExportDlg && (

        <div className="dialog-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}

          onMouseDown={e => { if (e.target === e.currentTarget) setShowExportDlg(false) }}>

          <ExportDialog

            content={exportMd}

            onClose={() => setShowExportDlg(false)}

            onCopy={copyExport}

            onDownload={downloadExport}

          />

        </div>

      )}



      {showDrawDlg && (

        <div className="dialog-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}

          onMouseDown={e => { if (e.target === e.currentTarget) setShowDrawDlg(false) }}>

          <DrawingBoard onClose={() => setShowDrawDlg(false)} />

        </div>

      )}



      {showKanbanDlg && (

        <div className="dialog-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}

          onMouseDown={e => { if (e.target === e.currentTarget) setShowKanbanDlg(false) }}>

          <KanbanBoard activeId={activeId} onClose={() => setShowKanbanDlg(false)} />

        </div>

      )}

    </>

  )

}



export default MeetingView