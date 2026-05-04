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

interface DayUsage {
  date: string
  total_requests: number
  total_prompt_tokens: number
  total_completion_tokens: number
  total_tokens: number
  total_cost: number
  avg_latency_ms: number
  by_agent: Record<string, {
    requests: number
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
    cost: number
  }>
}

const UsagePage: React.FC = () => {
  const { t } = useLanguage()
  const [usage, setUsage] = useState<DayUsage[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUsage()
  }, [])

  async function loadUsage() {
    setLoading(true)
    try {
      const res = await (window as any).agentAPI.getUsageStats(7)
      setUsage(res.days || [])
    } catch {} finally {
      setLoading(false)
    }
  }

  function formatNum(n: number) {
    return n.toLocaleString()
  }

  const totals = usage.reduce((acc, day) => ({
    requests: acc.requests + day.total_requests,
    prompt: acc.prompt + day.total_prompt_tokens,
    completion: acc.completion + day.total_completion_tokens,
    tokens: acc.tokens + day.total_tokens,
    cost: acc.cost + day.total_cost,
  }), { requests: 0, prompt: 0, completion: 0, tokens: 0, cost: 0 })

  return (
    <div style={{ padding: 16, maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: 18, color: 'var(--nb-text-primary)' }}>{t.usage.monitor}</h2>
        <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--nb-text-muted)' }}>
          {t.usage.description}
        </p>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--nb-text-primary)' }}>{t.usage.last7Days}</div>
        <button
          onClick={() => {
            const blob = new Blob([JSON.stringify(usage, null, 2)], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `usage-${new Date().toISOString().slice(0,10)}.json`
            a.click()
            URL.revokeObjectURL(url)
          }}
          style={{
            padding: '6px 12px', borderRadius: 6, fontSize: 12,
            background: 'transparent', color: 'var(--nb-text-muted)',
            border: '1px solid var(--nb-border-strong)', cursor: 'pointer'
          }}
        >{t.usage.export}</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: 12, marginBottom: 24 }}>
        {[
          { label: t.usage.totalRequests, value: formatNum(totals.requests), color: '#3b82f6' },
          { label: t.usage.promptTokens, value: formatNum(totals.prompt), color: '#8b5cf6' },
          { label: t.usage.completionTokens, value: formatNum(totals.completion), color: '#10b981' },
          { label: t.usage.totalTokens, value: formatNum(totals.tokens), color: '#f59e0b' },
        ].map(card => (
          <div key={card.label} style={{
            background: 'var(--nb-bg-secondary)', border: '1px solid var(--nb-border)',
            borderRadius: 8, padding: 16, textAlign: 'center'
          }}>
            <div style={{ fontSize: 11, color: 'var(--nb-text-muted)', marginBottom: 4 }}>{card.label}</div>
            <div style={{ fontSize: 20, fontWeight: 600, color: card.color }}>{card.value}</div>
          </div>
        ))}
      </div>

      {/* Daily Breakdown */}
      <div style={{
        background: 'var(--nb-bg-secondary)', border: '1px solid var(--nb-border)',
        borderRadius: 8, overflow: 'hidden', marginBottom: 24
      }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--nb-border)', fontSize: 13, fontWeight: 500, color: 'var(--nb-text-primary)' }}>
          {t.usage.dailyBreakdown}
        </div>
        {loading ? (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--nb-text-muted)' }}>{t.common.loading}</div>
        ) : usage.length === 0 ? (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--nb-text-muted)', fontSize: 13 }}>
            {t.usage.noData}
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ background: 'var(--nb-bg-primary)', borderBottom: '1px solid var(--nb-border)' }}>
                {['Date', 'Requests', 'Prompt Tokens', 'Completion Tokens', 'Total Tokens', 'Avg Latency'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--nb-text-muted)', fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {usage.map(day => (
                <tr key={day.date} style={{ borderBottom: '1px solid var(--nb-border)' }}>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-primary)' }}>{day.date}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(day.total_requests)}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(day.total_prompt_tokens)}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(day.total_completion_tokens)}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(day.total_tokens)}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{day.avg_latency_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Per-Agent Breakdown */}
      {usage.length > 0 && Object.keys(usage[usage.length - 1].by_agent || {}).length > 0 && (
        <div style={{
          background: 'var(--nb-bg-secondary)', border: '1px solid var(--nb-border)',
          borderRadius: 8, overflow: 'hidden'
        }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--nb-border)', fontSize: 13, fontWeight: 500, color: 'var(--nb-text-primary)' }}>
            Per-Agent Breakdown (Today)
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ background: 'var(--nb-bg-primary)', borderBottom: '1px solid var(--nb-border)' }}>
                {['Agent', 'Requests', 'Prompt Tokens', 'Completion Tokens', 'Total Tokens'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--nb-text-muted)', fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(usage[usage.length - 1].by_agent || {}).map(([agent, data]: [string, any]) => (
                <tr key={agent} style={{ borderBottom: '1px solid var(--nb-border)' }}>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-primary)' }}>{agent}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(data.requests)}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(data.prompt_tokens)}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(data.completion_tokens)}</td>
                  <td style={{ padding: '8px 12px', color: 'var(--nb-text-muted)' }}>{formatNum(data.total_tokens)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default UsagePage