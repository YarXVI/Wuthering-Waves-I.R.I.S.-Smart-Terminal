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
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import ChatView from '../components/ChatView'
import { Button } from '../components/ui'
import type { AgentInfo } from '../types'

const ChatPage: React.FC = () => {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [activeAgentId, setActiveAgentId] = useState('iris')
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [memragEnabled, setMemragEnabled] = useState(false)
  const navigate = useNavigate()
  const { toggleTheme, isDark } = useTheme()

  useEffect(() => {
    loadAgents()
    checkHealth()
    loadMemRAGStatus()
  }, [])

  useEffect(() => {
    const interval = setInterval(loadAgents, 2000)
    return () => clearInterval(interval)
  }, [])

  async function checkHealth() {
    try {
      const res = await window.agentAPI.health()
      setServerStatus(res.status === 'ok' ? 'online' : 'offline')
    } catch {
      setServerStatus('offline')
    }
  }

  async function loadAgents() {
    try {
      const res = await window.agentAPI.listAgents()
      if (res.agents?.length) setAgents(res.agents)
    } catch {}
  }

  async function loadMemRAGStatus() {
    try {
      const s = await window.agentAPI.getMemRAGStatus()
      setMemragEnabled(s.enabled)
    } catch {}
  }

  async function handleToggleMemRAG() {
    const next = !memragEnabled
    try {
      await window.agentAPI.toggleMemRAG(next)
      setMemragEnabled(next)
    } catch {}
  }

  async function handleReset(agentId?: string) {
    if (agentId) {
      await window.agentAPI.reset(agentId)
    } else {
      await window.agentAPI.resetAll()
    }
    loadAgents()
  }

  async function handleNewSession(agentId: string) {
    await window.agentAPI.newSession(agentId)
  }

  function switchAgent(agentId: string) {
    setActiveAgentId(agentId)
  }

  return (
    <ChatView
      agents={agents}
      activeAgentId={activeAgentId}
      onAgentChange={switchAgent}
      onReset={handleReset}
      onNewSession={handleNewSession}
      onToggleMemRAG={handleToggleMemRAG}
      memragEnabled={memragEnabled}
      serverStatus={serverStatus}
    />
  )
}

export default ChatPage