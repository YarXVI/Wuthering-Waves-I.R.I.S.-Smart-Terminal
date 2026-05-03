import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg'
  icon?: boolean
  loading?: boolean
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon = false,
  loading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClass = 'nb-btn'
  const variantClass = `nb-btn-${variant}`
  const sizeClass = size !== 'md' ? `nb-btn-${size}` : ''
  const iconClass = icon ? 'nb-btn-icon' : ''
  const classes = [baseClass, variantClass, sizeClass, iconClass, className].filter(Boolean).join(' ')

  return (
    <button
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span className="nb-animate-spin" style={{ width: 14, height: 14, border: '2px solid currentColor', borderTopColor: 'transparent', borderRadius: '50%', display: 'inline-block' }} />
      )}
      {children}
    </button>
  )
}

export default Button