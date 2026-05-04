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

interface AvatarProps {
  emoji?: string
  name: string
  size?: 'sm' | 'md' | 'lg'
  status?: 'online' | 'offline' | 'busy' | 'error'
  agentId?: string
}

export const Avatar: React.FC<AvatarProps> = ({
  emoji,
  name,
  size = 'md',
  status,
  agentId,
}) => {
  const sizeClass = size === 'sm' ? 'nb-avatar-sm' : size === 'lg' ? 'nb-avatar-lg' : ''
  const statusClass = status ? `nb-avatar-status ${status}` : ''

  let bgClass = 'nb-avatar-user'
  if (agentId === 'iris') bgClass = 'nb-avatar-iris'
  else if (agentId === 'codey') bgClass = 'nb-avatar-codey'
  else if (agentId === 'scribe') bgClass = 'nb-avatar-scribe'

  const initial = emoji || name.charAt(0).toUpperCase()

  return (
    <div className={`nb-avatar ${sizeClass} ${bgClass}`}>
      {initial}
      {status && <span className={statusClass} />}
    </div>
  )
}

export default Avatar