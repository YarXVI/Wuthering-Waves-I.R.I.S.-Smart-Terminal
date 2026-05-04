import React, { useState, useRef, useEffect, useMemo } from 'react'

import MarkdownContent from './MarkdownContent'

import { useWebSocket } from '../hooks'

import { useLanguage } from '../contexts/LanguageContext'

import { Button, Input } from './ui'



// Types

interface AgentInfo {

  id: string

  name: string

  emoji: string

  title: string

  status: 'idle' | 'thinking' | 'working' | 'error'

  current_task: string

  message_count: number

}



interface Message {

  role: 'user' | 'assistant'

  content: string

  agentId: string

  agentName: string

  timestamp: number

}



interface ChatViewProps {

  agents: AgentInfo[]

  activeAgentId: string

  onAgentChange: (id: string) => void

  onReset: (agentId?: string) => void

  onNewSession: (agentId: string) => void

  onToggleMemRAG: () => void

  memragEnabled: boolean

  serverStatus: 'checking' | 'online' | 'offline'

}



const AGENT_COLORS: Record<string, string> = {

  iris: 'nb-avatar-iris',

  codey: 'nb-avatar-codey',

  scribe: 'nb-avatar-scribe',

}



function formatTime(ts: number): string {

  const d = new Date(ts)

  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`

}



const STORAGE_KEY_PREFIX = 'chat_messages_'



const ChatView: React.FC<ChatViewProps> = ({

  agents,

  activeAgentId,

  onAgentChange,

  onReset,

  onNewSession,

  onToggleMemRAG,

  memragEnabled,

  serverStatus,

}) => {

  const { t } = useLanguage()

  

  // Load messages from localStorage on mount

  const [messages, setMessages] = useState<Message[]>(() => {

    try {

      const saved = localStorage.getItem(STORAGE_KEY_PREFIX + activeAgentId)

      return saved ? JSON.parse(saved) : []

    } catch {

      return []

    }

  })

  

  const [input, setInput] = useState('')

  const [loading, setLoading] = useState(false)

  const [notifications, setNotifications] = useState<string[]>([])

  const [showNotifications, setShowNotifications] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const clientId = useMemo(() => 'desktop-' + Math.random().toString(36).slice(2), [])

  const wsUrl = useMemo(() => `ws://127.0.0.1:8000/ws/notifications/${clientId}`, [clientId])

  const { status: wsStatus } = useWebSocket({

    url: wsUrl,

    debugName: 'ChatView',

    maxReconnectAttempts: 3,

    onMessage: (data) => {

      if (data.type === 'notification' && (data.message || data.title)) {

        setNotifications(prev => [data.message || data.title, ...prev].slice(0, 20))

      }

    },

  })



  const activeAgent = agents.find(a => a.id === activeAgentId)

  const currentMessages = messages.filter(m => m.agentId === activeAgentId)



  // Save messages to localStorage when changed

  useEffect(() => {

    try {

      localStorage.setItem(STORAGE_KEY_PREFIX + activeAgentId, JSON.stringify(messages))

    } catch {

      // Handle errors when saving to localStorage

    }

  }, [messages, activeAgentId])



  // Load messages when agent changes
  useEffect(() => {

    try {

      const saved = localStorage.getItem(STORAGE_KEY_PREFIX + activeAgentId)

      if (saved) {

        setMessages(JSON.parse(saved))

      }

    } catch {

      // Handle errors when loading from localStorage

    }

  }, [activeAgentId])



  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })

  }, [messages])



  async function handleSend() {

    const text = input.trim()

    if (!text || loading) return

    setInput('')



    const agent = agents.find(a => a.id === activeAgentId)

    const agentName = agent?.name || activeAgentId



    setMessages(prev => [

      ...prev,

      { role: 'user', content: text, agentId: activeAgentId, agentName: 'You', timestamp: Date.now() },

    ])



    setLoading(true)

    try {

      const res = await window.agentAPI.chat(text, activeAgentId)

      setMessages(prev => [

        ...prev,

        {

          role: 'assistant',

          content: res.reply,

          agentId: res.agent_id || activeAgentId,

          agentName: res.agent_name || agentName,

          timestamp: Date.now(),

        },

      ])

    } catch (e: any) {

      setMessages(prev => [

        ...prev,

        {

          role: 'assistant',

          content: `[Error] ${e.message}`,

          agentId: activeAgentId,

          agentName: 'System',

          timestamp: Date.now(),

        },

      ])

    }

    setLoading(false)

  }



  function clearLocalMessages(agentId: string) {

    try {

      localStorage.removeItem(STORAGE_KEY_PREFIX + agentId)

    } catch {

      // Handle errors when updating messages

    }

  }



  function handleResetWithStorage(agentId?: string) {

    if (agentId) {

      clearLocalMessages(agentId)

      // Delete messages for specific agent      setMessages(prev => prev.filter(m => m.agentId !== agentId))

      onReset(agentId)

    } else {

      // Delete messages for all agents      agents.forEach(a => clearLocalMessages(a.id))

      setMessages([])

      onReset()

    }

  }



  function handleNewSessionWithStorage(agentId: string) {

    clearLocalMessages(agentId)

    setMessages(prev => prev.filter(m => m.agentId !== agentId))

    onNewSession(agentId)

  }



  function handleKeyDown(e: React.KeyboardEvent) {

    if (e.key === 'Enter' && !e.shiftKey) {

      e.preventDefault()

      handleSend()

    }

  }



  return (

    <div className="chat-container" style={{ display: 'flex', height: '100%' }}>

      {/* Agent List Sidebar */}

      <aside className="chat-sidebar" style={{

        width: 260,

        minWidth: 260,

        height: '100%',

        background: 'var(--nb-bg-secondary)',

        borderRight: 'var(--nb-border)',

        display: 'flex',

        flexDirection: 'column',

      }}>

        <div style={{

          padding: 'var(--nb-space-md) var(--nb-space-lg)',

          borderBottom: 'var(--nb-border)',

          display: 'flex',

          alignItems: 'center',

          justifyContent: 'space-between',

        }}>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nb-space-sm)' }}>

            <div style={{

              width: 10, height: 10, borderRadius: '50%',

              background: serverStatus === 'online' ? 'var(--nb-success)' : 

                         serverStatus === 'offline' ? 'var(--nb-error)' : 'var(--nb-warning)',

              boxShadow: serverStatus === 'online' ? '0 0 8px var(--nb-success)' : 'none',

            }} />

            <span className="nb-text-base nb-font-semibold">{t.chat.agents}</span>

          </div>

          

          <div style={{ position: 'relative' }}>

            <Button

              variant="ghost"

              size="sm"

              icon

              onClick={() => setShowNotifications(v => !v)}

            >

              {t.chat.notifications}

              {notifications.length > 0 && <span style={{

                position: 'absolute', top: -4, right: -4,

                background: 'var(--nb-error)',

                width: 16, height: 16, borderRadius: '50%',

                fontSize: 10, lineHeight: '16px',

                textAlign: 'center',

                color: '#fff', fontWeight: 700,

              }}>{notifications.length}</span>}

            </Button>

            {showNotifications && (

              <div style={{

                position: 'absolute', right: 0, top: '100%', zIndex: 100,

                background: 'var(--nb-bg-secondary)',

                border: 'var(--nb-border)',

                borderRadius: 'var(--nb-radius-md)',

                padding: 'var(--nb-space-md)',

                minWidth: 220,

                maxWidth: 280,

                boxShadow: 'var(--nb-shadow-lg)',

                maxHeight: 300,

                overflow: 'auto',

              }}>

                <div className="nb-text-xs nb-text-secondary nb-text-muted nb-font-semibold" style={{ marginBottom: 'var(--nb-space-sm)' }}>{t.chat.notifications}</div>

                {notifications.length === 0 ? (

                  <div className="nb-text-sm nb-text-muted">{t.chat.noNotifications}</div>

                ) : notifications.map((n, i) => (

                  <div key={i} className="nb-text-xs" style={{

                    padding: 'var(--nb-space-xs) 0',

                    borderBottom: i < notifications.length -1 ? '1px solid var(--nb-border)' : 'none',

                  }}>{n}</div>

                ))}

              </div>

            )}

          </div>

        </div>



        <div className="nb-scroll" style={{ flex: 1, padding: 'var(--nb-space-sm)', overflowY: 'auto' }}>

          {agents.map(agent => (

            <button

              key={agent.id}

              onClick={() => onAgentChange(agent.id)}

              style={{

                width: '100%',

                padding: 'var(--nb-space-md)',

                marginBottom: 'var(--nb-space-xs)',

                background: agent.id === activeAgentId ? 'var(--nb-accent-bg)' : 'transparent',

                border: agent.id === activeAgentId ? '2px solid var(--nb-accent)' : '2px solid transparent',

                borderRadius: 'var(--nb-radius-lg)',

                cursor: 'pointer',

                textAlign: 'left',

                transition: 'all var(--nb-transition-fast)',

                display: 'flex',

                alignItems: 'flex-start',

                gap: 'var(--nb-space-md)',

              }}

            >

              <div className={`nb-avatar ${AGENT_COLORS[agent.id as keyof typeof AGENT_COLORS] || 'nb-avatar-iris'}`}>

                {agent.emoji}

              </div>

              <div style={{ flex: 1, minWidth: 0 }}>

                <div className="nb-text-sm nb-font-semibold nb-text-primary">

                  {agent.name}

                </div>

                <div className="nb-text-xs nb-text-tertiary" style={{ marginBottom: 'var(--nb-space-xs)' }}>

                  {agent.title}

                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nb-space-xs)' }}>

                  <div style={{

                    width: 6, height: 6, borderRadius: '50%',

                    background: agent.status === 'idle' ? 'var(--nb-success)' : 

                              agent.status === 'thinking' ? 'var(--nb-warning)' :

                              agent.status === 'working' ? 'var(--nb-info)' : 'var(--nb-error)',

                  }} />

                  <span className="nb-text-xs nb-text-muted" style={{ textTransform: 'uppercase' }}>

                    {t.status[agent.status]}

                  </span>

                  {agent.current_task && <span className="nb-text-xs nb-text-muted">📋 {agent.current_task.slice(0, 30)}{agent.current_task.length > 30 ? '...' : ''}</span>}

                </div>

              </div>

              {agent.message_count > 0 && <div className="nb-badge nb-badge-default nb-badge-accent" style={{ alignSelf: 'flex-start' }}>

                {agent.message_count}

              </div>}

            </button>

          ))}

        </div>



        <div style={{

          padding: 'var(--nb-space-md) var(--nb-space-lg)',

          borderTop: 'var(--nb-border)',

          display: 'flex',

          flexDirection: 'column',

          gap: 'var(--nb-space-sm)',

        }}>

          <div style={{ display: 'flex', gap: 'var(--nb-space-sm)' }}>

            <Button

              variant="secondary"

              size="sm"

              style={{ flex: 1 }}

              onClick={() => handleNewSessionWithStorage(activeAgentId)}

            >

                {t.chat.newChat}

            </Button>

            <Button

              variant="ghost"

              size="sm"

              onClick={() => handleResetWithStorage(activeAgentId)}

            >

              {t.chat.reset}

            </Button>

          </div>

          <Button

            variant={memragEnabled ? 'primary' : 'secondary'}

            size="sm"

            onClick={onToggleMemRAG}

            style={{ justifyContent: 'center' }}

          >

            {t.chat.notifications} {memragEnabled ? t.chat.memragOn : t.chat.memragOff}

          </Button>

        </div>

      </aside>



      {/* Input Area */}

      <main className="chat-main" style={{

        flex: 1,

        display: 'flex',

        flexDirection: 'column',

        minWidth: 0,

        background: 'var(--nb-bg-primary)',

      }}>

        <header className="chat-header" style={{

          height: 56,

          minHeight: 56,

          background: 'var(--nb-bg-secondary)',

          borderBottom: 'var(--nb-border)',

          display: 'flex',

          alignItems: 'center',

          padding: '0 var(--nb-space-lg)',

          gap: 'var(--nb-space-md)',

        }}>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nb-space-md)' }}>

            <div className={`nb-avatar nb-avatar-sm ${AGENT_COLORS[activeAgentId as keyof typeof AGENT_COLORS] || 'nb-avatar-iris'}`}>

              {activeAgent?.emoji || ''}

            </div>

            <div>

              <div className="nb-text-base nb-font-semibold">

                {activeAgent?.name || 'Agent'}

              </div>

              <div className="nb-text-xs nb-text-tertiary">

                {activeAgent?.title || ''}

              </div>

            </div>

          </div>

        </header>



        <div className="nb-content">

          {/* Messages Area */}

          <div className="nb-scroll" style={{

            flex: 1,

            overflowY: 'auto',

            padding: 'var(--nb-space-lg)',

            display: 'flex',

            flexDirection: 'column',

            gap: 'var(--nb-space-lg)',

          }}>

            {currentMessages.length === 0 ? (

              <div style={{

                flex: 1,

                display: 'flex',

                flexDirection: 'column',

                alignItems: 'center',

                justifyContent: 'center',

                textAlign: 'center',

                padding: 'var(--nb-space-2xl)',

              }}>

                <div className="nb-avatar nb-avatar-lg" style={{

                  marginBottom: 'var(--nb-space-lg)',

                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',

                }}>

                {activeAgent?.emoji || ''}

              </div>

              <div className="nb-text-lg nb-font-semibold" style={{ marginBottom: 'var(--nb-space-xs)' }}>

                {t.chat.startConversation}

              </div>

              <div className="nb-text-sm nb-text-secondary">

                {t.chat.typeBelow}

              </div>

            </div>

            ) : (

              currentMessages.map((msg, i) => (

                <div key={i} className={`nb-message ${msg.role}`}>

                  <div className="nb-message-avatar">

                    <div className={`nb-avatar ${msg.role === 'user' ? 'nb-avatar-user' : AGENT_COLORS[msg.agentId as keyof typeof AGENT_COLORS] || 'nb-avatar-iris'}`}>

                      {msg.role === 'assistant' ? (agents.find(a => a.id === msg.agentId)?.emoji || '?') : 'You'}

                    </div>

                  </div>

                  <div className="nb-message-content">

                    <div className="nb-message-header">

                      <span className="nb-message-name">{msg.agentName}</span>

                      <span className="nb-message-time">{formatTime(msg.timestamp)}</span>

                    </div>

                    <div className="nb-message-body">

                      {msg.role === 'assistant' ? <MarkdownContent content={msg.content} /> : msg.content}

                    </div>

                  </div>

                </div>

              ))

            )}



            {loading && (

              <div className="nb-message assistant">

                <div className="nb-message-avatar">

                  <div className={`nb-avatar ${AGENT_COLORS[activeAgentId as keyof typeof AGENT_COLORS] || 'nb-avatar-iris'}`}>

                    {activeAgent?.emoji || '?'}

                  </div>

                </div>

                <div className="nb-message-content">

                  <div className="nb-message-header">

                    <span className="nb-message-name">{activeAgent?.name || '...'}</span>

                  </div>

                  <div className="nb-message-body">

                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nb-space-xs)' }}>

                      {t.chat.thinking}

                      <div style={{ width: 4, height: 4, borderRadius: '50%', background: 'currentColor', animation: 'nb-pulse 1.4s ease-in-out infinite', animationDelay: '0s' }} />

                      <div style={{ width: 4, height: 4, borderRadius: '50%', background: 'currentColor', animation: 'nb-pulse 1.4s ease-in-out infinite', animationDelay: '0.2s' }} />

                      <div style={{ width: 4, height: 4, borderRadius: '50%', background: 'currentColor', animation: 'nb-pulse 1.4s ease-in-out infinite', animationDelay: '0.4s' }} />

                    </div>

                  </div>

                </div>

              </div>

            )}



            <div ref={messagesEndRef} />

          </div>



          {/* Tool Call Area */}

          <div style={{

            padding: 'var(--nb-space-lg)',

            borderTop: 'var(--nb-border)',

            background: 'var(--nb-bg-secondary)',

          }}>

            <div style={{ display: 'flex', gap: 'var(--nb-space-md)', alignItems: 'flex-end' }}>

              <textarea

                className="nb-input"

                style={{

                  flex: 1,

                  resize: 'none',

                  minHeight: 60,

                  maxHeight: 140,

                }}

                placeholder={t.chat.placeholder}

                value={input}

                onChange={e => setInput(e.target.value)}

                onKeyDown={handleKeyDown}

                rows={2}

                disabled={loading}

              />

              <Button

                variant="primary"

                style={{

                  height: 60,

                  padding: '0 var(--nb-space-xl)',

                }}

                onClick={handleSend}

                disabled={loading || !input.trim()}

              >

                {t.chat.send}

              </Button>

            </div>

          </div>

        </div>

      </main>

    </div>

  )

}



export default ChatView