import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  hint,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{
            fontSize: 12,
            fontWeight: 600,
            color: 'var(--nb-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`nb-input ${error ? 'nb-input-error' : ''} ${className}`}
        {...props}
      />
      {hint && !error && (
        <span style={{ fontSize: 11, color: 'var(--nb-text-muted)' }}>{hint}</span>
      )}
      {error && (
        <span style={{ fontSize: 11, color: 'var(--nb-error)' }}>{error}</span>
      )}
    </div>
  )
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  className = '',
  id,
  ...props
}) => {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && (
        <label
          htmlFor={textareaId}
          style={{
            fontSize: 12,
            fontWeight: 600,
            color: 'var(--nb-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}
        >
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        className={`nb-input nb-textarea ${error ? 'nb-input-error' : ''} ${className}`}
        {...props}
      />
      {error && (
        <span style={{ fontSize: 11, color: 'var(--nb-error)' }}>{error}</span>
      )}
    </div>
  )
}

export default Input