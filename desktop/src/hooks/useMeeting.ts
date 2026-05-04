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

import { useState, useCallback, useEffect } from 'react'

export interface MeetingRoom {
  room_id: string
  topic?: string
  round_count?: number
  status?: string
  consensus?: boolean
  entry_count?: number
}

export interface MeetingStats {
  total_meetings: number
  completed: number
  consensus_reached: number
  total_rounds: number
}

export interface MeetingTemplate {
  id: string
  name: string
  description: string
  suggested_agents: string[]
  default_rounds: number
}

export interface UseMeetingReturn {
  rooms: MeetingRoom[]
  activeId: string | null
  setActiveId: (id: string | null) => void
  stats: MeetingStats | null
  templates: MeetingTemplate[]
  loading: boolean
  error: string | null
  loadRooms: (q?: string) => Promise<void>
  loadStats: () => Promise<void>
  loadTemplates: () => Promise<void>
  startMeeting: (topic: string, agents: string[]) => Promise<any>
  deleteMeeting: (roomId: string) => Promise<boolean>
  startDiscuss: (roomId: string) => Promise<any>
  judgeConsensus: (roomId: string) => Promise<any>
  summarizeMeeting: (roomId: string) => Promise<any>
  addWhiteboardEntry: (roomId: string, type: string, content: string) => Promise<void>
  getWhiteboard: (roomId: string) => Promise<any>
  getWhiteboardStats: (roomId: string) => Promise<any>
  createTemplate: (name: string, description: string, suggestedAgents: string[], defaultRounds: number) => Promise<any>
  updateTemplate: (templateId: string, name: string, description: string, suggestedAgents: string[], defaultRounds: number) => Promise<any>
  deleteTemplate: (templateId: string) => Promise<any>
  searchMeetings: (query: string) => Promise<any>
  listWhiteboardRooms: () => Promise<any>
}

const API = window as any

export function useMeeting(): UseMeetingReturn {
  const [rooms, setRooms] = useState<MeetingRoom[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [stats, setStats] = useState<MeetingStats | null>(null)
  const [templates, setTemplates] = useState<MeetingTemplate[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadTemplates = useCallback(async () => {
    try {
      const res = await API.agentAPI.listTemplates()
      setTemplates(res.templates || [])
    } catch {}
  }, [])

  const loadStats = useCallback(async () => {
    try {
      const statsData = await API.agentAPI.getMeetingStats()
      setStats(statsData)
    } catch {}
  }, [])

  const loadRooms = useCallback(async (q?: string) => {
    try {
      let res
      if (q?.trim()) {
        res = await API.agentAPI.searchMeetings(q.trim())
      } else {
        const m = await API.agentAPI.listMeetings()
        res = { meetings: m.meetings || [] }
      }
      let list: MeetingRoom[] = (res.meetings || []).map((m: any) => ({ ...m, entry_count: 0 }))
      const ids = await API.agentAPI.listWhiteboardRooms()
      if (ids.rooms) {
        const counts = Object.fromEntries((ids.rooms as any[]).map((r: any) => [r.room_id, r.entry_count]))
        list = list.map(r => ({ ...r, entry_count: counts[r.room_id] || 0 }))
      }
      setRooms(list)
    } catch {}
  }, [])

  const startMeeting = useCallback(async (topic: string, agents: string[]) => {
    setLoading(true)
    setError(null)
    try {
      const created = await API.agentAPI.startMeetingV2(topic, agents)
      await loadRooms()
      return created
    } catch (e: any) {
      setError(e.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [loadRooms])

  const deleteMeeting = useCallback(async (roomId: string) => {
    setLoading(true)
    setError(null)
    try {
      await API.agentAPI.deleteMeeting(roomId)
      if (activeId === roomId) setActiveId(null)
      await loadRooms()
      await loadStats()
      return true
    } catch (e: any) {
      setError(e.message)
      return false
    } finally {
      setLoading(false)
    }
  }, [loadRooms, loadStats, activeId])

  const startDiscuss = useCallback(async (roomId: string) => {
    try {
      const r = await API.agentAPI.autoDiscuss(roomId, 10)
      return r
    } catch (e: any) {
      setError(e.message)
      return null
    }
  }, [])

  const judgeConsensus = useCallback(async (roomId: string) => {
    try {
      const r = await API.agentAPI.judgeMeetingConsensus(roomId)
      return r
    } catch (e: any) {
      setError(e.message)
      return null
    }
  }, [])

  const summarizeMeeting = useCallback(async (roomId: string) => {
    try {
      const r = await API.agentAPI.summarizeMeeting(roomId)
      return r
    } catch (e: any) {
      setError(e.message)
      return null
    }
  }, [])

  const addWhiteboardEntry = useCallback(async (roomId: string, type: string, content: string) => {
    try {
      await API.agentAPI.addWhiteboardEntry(roomId, type, content)
    } catch {}
  }, [])

  const getWhiteboard = useCallback(async (roomId: string) => {
    try {
      return await API.agentAPI.getWhiteboard(roomId)
    } catch {
      return { entries: [] }
    }
  }, [])

  const getWhiteboardStats = useCallback(async (roomId: string) => {
    try {
      return await API.agentAPI.getWhiteboardStats(roomId)
    } catch {
      return null
    }
  }, [])

  const createTemplate = useCallback(async (name: string, description: string, suggestedAgents: string[], defaultRounds: number) => {
    try {
      return await API.agentAPI.createTemplate(name, description, suggestedAgents, defaultRounds)
    } catch {}
  }, [])

  const updateTemplate = useCallback(async (templateId: string, name: string, description: string, suggestedAgents: string[], defaultRounds: number) => {
    try {
      return await API.agentAPI.updateTemplate(templateId, name, description, suggestedAgents, defaultRounds)
    } catch {}
  }, [])

  const deleteTemplate = useCallback(async (templateId: string) => {
    try {
      return await API.agentAPI.deleteTemplate(templateId)
    } catch {}
  }, [])

  const searchMeetings = useCallback(async (query: string) => {
    try {
      return await API.agentAPI.searchMeetings(query)
    } catch {
      return { meetings: [] }
    }
  }, [])

  const listWhiteboardRooms = useCallback(async () => {
    try {
      return await API.agentAPI.listWhiteboardRooms()
    } catch {
      return { rooms: [] }
    }
  }, [])

  useEffect(() => {
    loadRooms()
    loadStats()
    loadTemplates()
  }, [loadRooms, loadStats, loadTemplates])

  return {
    rooms,
    activeId,
    setActiveId,
    stats,
    templates,
    loading,
    error,
    loadRooms,
    loadStats,
    loadTemplates,
    startMeeting,
    deleteMeeting,
    startDiscuss,
    judgeConsensus,
    summarizeMeeting,
    addWhiteboardEntry,
    getWhiteboard,
    getWhiteboardStats,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    searchMeetings,
    listWhiteboardRooms,
  }
}