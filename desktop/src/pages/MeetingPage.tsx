import React, { useState, useEffect } from 'react'

import { useNavigate } from 'react-router-dom'

import { useTheme } from '../contexts/ThemeContext'

import { useLanguage } from '../contexts/LanguageContext'

import MeetingView from '../components/MeetingView'

import { Button } from '../components/ui'

import type { AgentInfo } from '../types'



const MeetingPage: React.FC = () => {

  const { t } = useLanguage()

  const [agents, setAgents] = useState<AgentInfo[]>([])

  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const [apiAvailable, setApiAvailable] = useState(true)

  const navigate = useNavigate()

  const { toggleTheme, isDark } = useTheme()



  useEffect(() => {

    // Wait for agentAPI to be ready

    if (!window.agentAPI) {

      setApiAvailable(false)

      setServerStatus('offline')

      return

    }

    loadAgents()

    checkHealth()

  }, [])



  useEffect(() => {

    if (!apiAvailable) return

    const interval = setInterval(loadAgents, 5000)

    return () => clearInterval(interval)

  }, [apiAvailable])



  async function loadAgents() {

    try {

      const res = await window.agentAPI.listAgents()

      if (res.agents?.length) setAgents(res.agents)

    } catch {

      setServerStatus('offline')

    }

  }



  async function checkHealth() {

    try {

      const res = await window.agentAPI.health()

      setServerStatus(res.status === 'ok' ? 'online' : 'offline')

    } catch {

      setServerStatus('offline')

    }

  }



  const getStatusColor = (status: string) => {

    switch (status) {

      case 'online': return 'var(--nb-success)'

      case 'offline': return 'var(--nb-error)'

      default: return 'var(--nb-warning)'

    }

  }



  return (

    <div className="nb-layout">

      <aside className={`nb-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>

        <div style={{

          padding: 'var(--nb-space-md) var(--nb-space-lg)',

          borderBottom: 'var(--nb-border)',

          display: 'flex',

          alignItems: 'center',

          justifyContent: 'space-between',

        }}>

          {!sidebarCollapsed && (

            <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--nb-text-primary)' }}>

              {t.meeting.title}

            </span>

          )}

          <Button

            variant="ghost"

            size="sm"

            icon

            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}

            title={sidebarCollapsed ? t.meeting.expand : t.meeting.collapse}

          >

            {sidebarCollapsed ? '>' : '<'}

          </Button>

        </div>



        {!sidebarCollapsed && (

          <div style={{ padding: 'var(--nb-space-md) var(--nb-space-lg)', borderBottom: 'var(--nb-border)' }}>

            <Button

              variant="primary"

              className="nb-w-full"

              onClick={() => {}}

            >

              + {t.meeting.newMeeting}

            </Button>

          </div>

        )}

      </aside>



      <main className="nb-main">

        <header className="nb-header">

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nb-space-md)' }}>

            <div style={{

              width: 10,

              height: 10,

              borderRadius: '50%',

              background: getStatusColor(serverStatus),

              boxShadow: serverStatus === 'online' ? '0 0 8px var(--nb-success)' : 'none',

            }} />

            <div>

              <div style={{ fontSize: 14, fontWeight: 600 }}>{t.meeting.title}</div>

              <div style={{ fontSize: 11, color: 'var(--nb-text-tertiary)' }}>

                {serverStatus === 'online' ? t.meeting.ready : t.meeting.offline}

              </div>

            </div>

          </div>



          <div style={{ marginLeft: 'auto', display: 'flex', gap: 'var(--nb-space-sm)' }}>

            <Button

              variant="ghost"

              icon

              onClick={() => navigate('/')}

              title="Chat"

            >

              💬

            </Button>

            <Button

              variant="ghost"

              icon

              onClick={toggleTheme}

              title={isDark ? 'Light Mode' : 'Dark Mode'}

            >

              {isDark ? 'Light' : 'Dark'}

            </Button>

            <Button

              variant="ghost"

              icon

              onClick={() => navigate('/settings')}

              title="Settings"

            >

              ⚙️

            </Button>

          </div>

        </header>



        <div className="nb-content">

          {!apiAvailable ? (

            <div style={{

              display: 'flex',

              flexDirection: 'column',

              alignItems: 'center',

              justifyContent: 'center',

              height: '400px',

              textAlign: 'center',

            }}>

              <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>

              <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--nb-text-primary)', marginBottom: 8 }}>

                {t.meeting.apiUnavailable}

              </div>

              <div style={{ fontSize: 13, color: 'var(--nb-text-muted)', maxWidth: 400 }}>

                {t.meeting.apiUnavailableDesc}

              </div>

            </div>

          ) : (

            <MeetingView agents={agents} />

          )}

        </div>

      </main>

    </div>

  )

}



export default MeetingPage