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

// Shared utility functions

const AGENT_COLORS: Record<string, string> = {
  iris: '#4f46e5',
  codey: '#059669',
  scribe: '#d97706',
}

export function agentColor(agentId: string): string {
  return AGENT_COLORS[agentId] || '#6366f1'
}

export function formatTime(ts: number): string {
  const d = new Date(ts)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

export function authorName(author: string): string {
  const names: Record<string, string> = {
    system: 'System',
    iris: '馃 iris',
    codey: '馃捇 Codey',
    scribe: '馃摑 Scribe'
  }
  return names[author] || author
}

export function getEmoji(author: string): string {
  const emojis: Record<string, string> = {
    system: '馃搶',
    iris: '馃',
    codey: '馃捇',
    scribe: '馃摑'
  }
  return emojis[author] || '?'
}

export function getAuthorColor(author: string): string {
  const colors: Record<string, string> = {
    system: 'var(--c-system)',
    iris: 'var(--c-iris)',
    codey: 'var(--c-codey)',
    scribe: 'var(--c-scribe)'
  }
  return colors[author] || '#6366f1'
}
