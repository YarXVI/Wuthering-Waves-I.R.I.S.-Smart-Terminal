import React, { useState, useRef, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

interface AgentInfo {
  id: string
  name: string
  title: string
  emoji: string
}

interface Template {
  id: string
  name: string
  description: string
  suggested_agents: string[]
  default_rounds: number
}

interface NewMeetingDialogProps {
  agents: AgentInfo[]
  templates: Template[]
  onClose: () => void
  onStart: (topic: string, agents: string[]) => void
}

export default function NewMeetingDialog({ agents, templates, onClose, onStart }: NewMeetingDialogProps) {
  const { t } = useLanguage()
  const [topic, setTopic] = useState('')
  const [tplId, setTplId] = useState('')
  const [suggested, setSuggested] = useState<AgentInfo[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [reasoning, setReasoning] = useState('')
  const topicInputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    setTimeout(() => topicInputRef.current?.focus(), 50)
  }, [])

  async function suggest(templateId: string) {
    const tpl = templates.find(t => t.id === templateId)
    if (!tpl) return
    const prompt = `Meeting topic: "${topic || templateId}"
Available agents: ${agents.filter(a => a.id !== 'iris').map(a => `${a.id}: ${a.name} (${a.title})`).join(', ')}
Task: Recommend 2-4 agents best suited for this meeting.
Return JSON: {"suggested": ["agent_id1", "agent_id2"], "reasoning": "..."}`
    try {
      const res = await fetch('http://127.0.0.1:8765/meetings/suggest-agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      })
      const data = await res.json()
      if (data.suggested) {
        const sug = (data.suggested as string[])
          .map(id => agents.find(a => a.id === id))
          .filter(Boolean) as AgentInfo[]
        setSuggested(sug)
        setSelected(sug.map(a => a.id))
        setReasoning(data.reasoning || '')
      }
    } catch {}
  }

  function toggleAgent(id: string) {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  function handleStart() {
    if (!topic.trim()) return
    onStart(topic.trim(), selected)
  }

  return (
    <div className="dialog">
      <div className="dialog-title">{t.meeting.newMeeting}</div>
      <div className="dialog-desc">{t.meeting.chooseTemplate}</div>
      <select
        style={{
          width: '100%',
          background: 'var(--nb-bg-secondary)',
          border: '1px solid var(--nb-border-strong)',
          borderRadius: 8,
          color: 'var(--nb-text-primary)',
          fontSize: 13,
          padding: '7px 10px',
          outline: 'none',
          fontFamily: 'inherit',
          marginBottom: 8,
        }}
        value={tplId}
        onChange={e => {
          setTplId(e.target.value)
          if (e.target.value) {
            setTopic(topic || e.target.value)
            suggest(e.target.value)
          }
        }}
      >
        <option value="">{t.meeting.customNoTemplate}</option>
        {templates.map(t => (
          <option key={t.id} value={t.id}>{t.name} â€?{t.description}</option>
        ))}
      </select>
      <textarea
        ref={topicInputRef}
        className="dialog-input"
        placeholder={t.meeting.topicPlaceholder}
        value={topic}
        rows={3}
        onChange={e => setTopic(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleStart() } }}
      />
      {suggested.length > 0 && (
        <div className="dialog-agent-select">
          <div className="dialog-desc" style={{ marginTop: 8 }}>
            {t.meeting.recommended}: {reasoning && <span className="dialog-hint"> â€?{reasoning}</span>}
          </div>
          {suggested.map(a => (
            <label key={a.id} className="dialog-agent-item">
              <input
                type="checkbox"
                checked={selected.includes(a.id)}
                onChange={() => toggleAgent(a.id)}
              />
              <span className="agent-check-emoji">{a.emoji}</span>
              <span className="agent-check-name">{a.name}</span>
              <span className="agent-check-title">{a.title}</span>
            </label>
          ))}
        </div>
      )}
      <div className="dialog-actions">
        <button className="dialog-btn-cancel" onClick={onClose}>{t.common.cancel}</button>
        <button className="dialog-btn-confirm" onClick={handleStart} disabled={!topic.trim()}>{t.meeting.start}</button>
      </div>
    </div>
  )
}
