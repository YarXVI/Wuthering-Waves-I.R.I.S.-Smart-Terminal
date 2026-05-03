import React, { useState } from 'react'

interface ThinkingProcessProps {
  content: string
  author?: string
}

export const ThinkingProcess: React.FC<ThinkingProcessProps> = ({ content, author }) => {
  const [expanded, setExpanded] = useState(false)

  return (
    <details style={{ marginBottom: 6, marginTop: 4 }}>
      <summary
        style={{
          cursor: 'pointer',
          fontSize: 11,
          color: 'var(--nb-text-muted)',
          userSelect: 'none',
          display: 'flex',
          alignItems: 'center',
          gap: 4,
        }}
        onClick={(e) => {
          e.preventDefault()
          setExpanded(!expanded)
        }}
      >
        <span style={{
          transition: 'transform 0.2s',
          transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)',
          display: 'inline-block'
        }}>
          â–?        </span>
        ðŸ’­ Thinking Process {author && `- ${author}`}
      </summary>
      <div style={{
        marginTop: 6,
        padding: '8px 12px',
        background: 'var(--nb-bg-inset)',
        borderRadius: 6,
        fontSize: 12,
        color: 'var(--nb-text-secondary)',
        whiteSpace: 'pre-wrap',
        maxHeight: expanded ? 'none' : 200,
        overflowY: 'auto',
        border: '1px solid var(--nb-border)',
        lineHeight: 1.6,
      }}>
        {content}
      </div>
    </details>
  )
}

export default ThinkingProcess