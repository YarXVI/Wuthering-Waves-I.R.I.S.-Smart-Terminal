import React from 'react'

interface ErrorBannerProps {
  message: string | null
  onDismiss?: () => void
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss }) => {
  if (!message) return null

  return (
    <div style={{
      padding: '10px 16px',
      background: 'rgba(248, 113, 113, 0.15)',
      border: '1px solid rgba(248, 113, 113, 0.4)',
      borderRadius: 8,
      margin: '8px 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      fontSize: 13,
      color: '#f87171',
    }}>
      <span>⚠️ {message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#f87171',
            cursor: 'pointer',
            fontSize: 16,
            padding: '0 4px',
          }}
        >
          �?        </button>
      )}
    </div>
  )
}

interface LoadingOverlayProps {
  message?: string
  fullScreen?: boolean
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = 'Loading...',
  fullScreen = false
}) => {
  return (
    <div style={{
      position: fullScreen ? 'fixed' : 'absolute',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        width: 40,
        height: 40,
        border: '3px solid var(--nb-border)',
        borderTopColor: 'var(--nb-accent)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      {message && (
        <span style={{
          marginTop: 12,
          fontSize: 13,
          color: 'var(--nb-text-primary)',
        }}>
          {message}
        </span>
      )}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

interface EmptyStateProps {
  icon?: string
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = '📭',
  title,
  description,
  action,
}) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 40,
      textAlign: 'center',
    }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>{icon}</div>
      <div style={{ fontSize: 15, fontWeight: 500, marginBottom: 8 }}>{title}</div>
      {description && (
        <div style={{ fontSize: 13, color: 'var(--nb-text-muted)', marginBottom: 16 }}>
          {description}
        </div>
      )}
      {action && (
        <button
          onClick={action.onClick}
          style={{
            padding: '8px 16px',
            background: 'var(--nb-accent)',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 13,
          }}
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

export default ErrorBanner