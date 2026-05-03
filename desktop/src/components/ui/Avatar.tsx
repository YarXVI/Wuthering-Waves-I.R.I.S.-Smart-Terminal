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