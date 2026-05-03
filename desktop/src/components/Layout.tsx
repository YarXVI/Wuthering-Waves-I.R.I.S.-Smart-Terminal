import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'
import { Button } from './ui'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { toggleTheme, isDark } = useTheme()
  const { t } = useLanguage()

  const currentPath = location.pathname

  const navItems = [
    { path: '/', label: t.app.chat, icon: '💬' },
    { path: '/meeting', label: t.app.meeting, icon: '🏛�? },
    { path: '/workflow', label: t.app.workflow, icon: '⚙️' },
    { path: '/history', label: t.app.history, icon: '📜' },
    { path: '/usage', label: t.app.usage, icon: '📊' },
  ]

  return (
    <div className="nb-root" style={{ height: '100vh', display: 'flex' }}>
      {/* 全局侧边导航 */}
      <aside className="nb-sidebar" style={{ width: 60, minWidth: 60, flexShrink: 0 }}>
        <div style={{
          padding: 'var(--nb-space-lg) var(--nb-space-md)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: 'var(--nb-border)',
        }}>
          <div className="nb-avatar" style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            fontSize: 20,
          }}>
            🤖
          </div>
        </div>

        <nav style={{
          flex: 1,
          padding: 'var(--nb-space-md) 0',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 'var(--nb-space-sm)',
        }}>
          {navItems.map(item => (
            <Button
              key={item.path}
              variant={currentPath === item.path ? 'primary' : 'ghost'}
              size="sm"
              icon
              onClick={() => navigate(item.path)}
              title={item.label}
              style={{
                width: 40,
                height: 40,
                borderRadius: 'var(--nb-radius-md)',
                fontSize: 18,
              }}
            >
              {item.icon}
            </Button>
          ))}
        </nav>

        <div style={{
          padding: 'var(--nb-space-md) 0',
          borderTop: 'var(--nb-border)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 'var(--nb-space-sm)',
        }}>
          <Button
            variant="ghost"
            size="sm"
            icon
            onClick={toggleTheme}
            title={isDark ? t.settings.lightMode : t.settings.darkMode}
          >
            {isDark ? '☀�? : '🌙'}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            icon
            onClick={() => navigate('/settings')}
            title={t.app.settings}
          >
            ⚙️
          </Button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main style={{ flex: 1, overflow: 'hidden' }}>
        {children}
      </main>
    </div>
  )
}

export default Layout