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