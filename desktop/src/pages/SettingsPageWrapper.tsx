import React from 'react'
import { useNavigate } from 'react-router-dom'
import SettingsPage from '../SettingsPage'

const SettingsPageWrapper: React.FC = () => {
  const navigate = useNavigate()
  return <SettingsPage onClose={() => navigate(-1)} />
}

export default SettingsPageWrapper
