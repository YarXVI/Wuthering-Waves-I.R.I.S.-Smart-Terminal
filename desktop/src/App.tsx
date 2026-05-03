import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import './styles/neo-brutalist.css'
import { ThemeProvider } from './contexts/ThemeContext'
import { LanguageProvider } from './contexts/LanguageContext'
import { ModuleProvider } from './contexts/ModuleContext'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import MeetingPage from './pages/MeetingPage'
import SettingsPageWrapper from './pages/SettingsPageWrapper'
import WorkflowPage from './pages/WorkflowPage'
import HistoryPage from './pages/HistoryPage'
import UsagePage from './pages/UsagePage'

function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <ModuleProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<ChatPage />} />
              <Route path="/meeting" element={<MeetingPage />} />
              <Route path="/settings" element={<SettingsPageWrapper />} />
              <Route path="/workflow" element={<WorkflowPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/usage" element={<UsagePage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        </ModuleProvider>
      </LanguageProvider>
    </ThemeProvider>
  )
}

export default App