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