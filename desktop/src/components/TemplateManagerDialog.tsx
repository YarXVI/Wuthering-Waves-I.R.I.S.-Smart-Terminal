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

import React, { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

interface Agent {
  id: string
  name: string
  emoji: string
}

interface Template {
  id: string
  name: string
  description: string
  suggested_agents: string[]
  default_rounds: number
}

interface TemplateManagerDialogProps {
  templates: Template[]
  agents: Agent[]
  onClose: () => void
  onCreate: (tpl: Omit<Template, 'id'>) => void
  onUpdate: (id: string, tpl: Omit<Template, 'id'>) => void
  onDelete: (id: string) => void
}

export default function TemplateManagerDialog({ templates, agents, onClose, onCreate, onUpdate, onDelete }: TemplateManagerDialogProps) {
  const { t } = useLanguage()
  const [editingId, setEditingId] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [rounds, setRounds] = useState(6)

  const editingTpl = editingId ? templates.find(t => t.id === editingId) : null

  useEffect(() => {
    if (editingTpl) {
      setName(editingTpl.name)
      setDesc(editingTpl.description)
      setSelectedAgents(editingTpl.suggested_agents)
      setRounds(editingTpl.default_rounds)
    } else {
      setName('')
      setDesc('')
      setSelectedAgents([])
      setRounds(6)
    }
  }, [editingId])

  function toggleAgent(id: string) {
    setSelectedAgents(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  function handleSave() {
    if (!name.trim()) return
    const data = { name: name.trim(), description: desc.trim(), suggested_agents: selectedAgents, default_rounds: rounds }
    if (editingId) {
      onUpdate(editingId, data)
      setEditingId(null)
    } else {
      onCreate(data)
      setName(''); setDesc(''); setSelectedAgents([]); setRounds(6)
    }
  }

  const PROTECTED = ['tech-review', 'planning', 'postmortem', 'brainstorm']

  return (
    <div className="dialog" style={{ width: '90%', maxWidth: 520, maxHeight: '85vh', overflowY: 'auto' }}>
      <div className="dialog-title">{t.meeting.manageTemplates}</div>

      <div style={{ marginBottom: 12 }}>
        {templates.map(t => (
          <div
            key={t.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px',
              border: '1px solid var(--nb-border-strong)',
              borderRadius: 8,
              marginBottom: 6,
              background: 'var(--nb-bg-tertiary)',
            }}
          >
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 500, fontSize: 13, color: 'var(--nb-text-primary)' }}>{t.name}</div>
              <div style={{ fontSize: 11, color: 'var(--nb-text-muted)', marginTop: 2 }}>{t.description}</div>
              <div style={{ fontSize: 10, color: 'var(--nb-text-muted)', marginTop: 2 }}>
                {t.meeting.agents}: {t.suggested_agents.join(', ')} · {t.default_rounds} {t.meeting.rounds}
              </div>
            </div>
            <div style={{ display: 'flex', gap: 6, marginLeft: 10, flexShrink: 0 }}>
              <button
                style={{
                  padding: '4px 10px',
                  fontSize: 11,
                  borderRadius: 6,
                  border: '1px solid var(--nb-border-strong)',
                  background: 'transparent',
                  cursor: 'pointer',
                  color: 'var(--nb-text-muted)',
                }}
                onClick={() => setEditingId(t.id)}
              >
                {t.meeting.edit}
              </button>
              {!PROTECTED.includes(t.id) && (
                <button
                  style={{
                    padding: '4px 10px',
                    fontSize: 11,
                    borderRadius: 6,
                    border: '1px solid rgba(248,113,113,0.3)',
                    background: 'transparent',
                    cursor: 'pointer',
                    color: '#f87171',
                  }}
                  onClick={() => onDelete(t.id)}
                >
                  {t.meeting.delete}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <div style={{ borderTop: '1px solid var(--nb-border)', paddingTop: 12 }}>
        <div className="dialog-title" style={{ fontSize: 14, marginBottom: 8, color: 'var(--nb-text-primary)' }}>
          {editingId ? t.meeting.editTemplate : t.meeting.newTemplate}
        </div>
        <input
          className="dialog-input"
          style={{ marginBottom: 8 }}
          placeholder={t.meeting.templateNamePlaceholder}
          value={name}
          onChange={e => setName(e.target.value)}
        />
        <textarea
          className="dialog-input"
          style={{ marginBottom: 8 }}
          placeholder={t.meeting.descriptionPlaceholder}
          rows={2}
          value={desc}
          onChange={e => setDesc(e.target.value)}
        />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 8 }}>
          <div style={{ fontSize: 12, color: 'var(--nb-text-muted)' }}>{t.meeting.suggestedAgents}:</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {agents.filter(a => a.id !== 'iris').map(a => (
              <label
                key={a.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  cursor: 'pointer',
                  fontSize: 12,
                  background: 'var(--nb-bg-secondary)',
                  padding: '5px 10px',
                  borderRadius: 6,
                  border: '1px solid var(--nb-border-strong)',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedAgents.includes(a.id)}
                  onChange={() => toggleAgent(a.id)}
                />
                <span style={{ fontSize: 14 }}>{a.emoji}</span>
                <span>{a.name}</span>
              </label>
            ))}
          </div>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label style={{ fontSize: 12, color: 'var(--nb-text-muted)', display: 'block', marginBottom: 4 }}>
            {t.meeting.defaultRounds}:
          </label>
          <input
            type="number"
            min={1}
            max={20}
            value={rounds}
            onChange={e => setRounds(parseInt(e.target.value) || 6)}
            style={{
              width: 100,
              padding: '6px 10px',
              borderRadius: 6,
              border: '1px solid var(--nb-border-strong)',
              background: 'var(--nb-bg-secondary)',
              color: 'var(--nb-text-primary)',
              fontSize: 13,
            }}
          />
        </div>
        <div className="dialog-actions">
          <button
            className="dialog-btn-cancel"
            onClick={() => { onClose() }}
          >
            {t.meeting.cancel}
          </button>
          <button
            className="dialog-btn-confirm"
            onClick={handleSave}
            disabled={!name.trim()}
          >
            {editingId ? t.meeting.update : t.meeting.create}
          </button>
        </div>
      </div>
    </div>
  )
}
