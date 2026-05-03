import React from 'react'
import Avatar from './Avatar'

interface MessageProps {
  role: 'user' | 'assistant'
  name: string
  content: React.ReactNode
  timestamp?: number
  agentId?: string
  emoji?: string
}

export const Message: React.FC<MessageProps> = ({
  role,
  name,
  content,
  timestamp,
  agentId,
  emoji,
}) => {
  const timeStr = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : ''

  return (
    <div className={`nb-message ${role}`}>
      <div className="nb-message-avatar">
        <Avatar name={name} agentId={agentId} emoji={emoji} size="sm" />
      </div>
      <div className="nb-message-content">
        <div className="nb-message-header">
          <span className="nb-message-name">{name}</span>
          {timeStr && <span className="nb-message-time">{timeStr}</span>}
        </div>
        <div className="nb-message-body">{content}</div>
      </div>
    </div>
  )
}

export default Message