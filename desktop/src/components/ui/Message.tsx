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