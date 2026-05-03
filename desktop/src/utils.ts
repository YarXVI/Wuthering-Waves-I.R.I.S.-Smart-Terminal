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
    iris: '🧠 iris',
    codey: '💻 Codey',
    scribe: '📝 Scribe'
  }
  return names[author] || author
}

export function getEmoji(author: string): string {
  const emojis: Record<string, string> = {
    system: '📌',
    iris: '🧠',
    codey: '💻',
    scribe: '📝'
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
