import React, { createContext, useContext, useState, useCallback } from 'react'

export interface Module {
  id: string
  name: string
  version: string
  author: string
  description?: string
  enabled: boolean
  priority?: number
}

export interface ModuleAPI {
  registerModule: (module: Module) => boolean
  unregisterModule: (moduleId: string) => boolean
  enableModule: (moduleId: string) => void
  disableModule: (moduleId: string) => void
  getModule: (moduleId: string) => Module | undefined
  getAllModules: () => Module[]
  getEnabledModules: () => Module[]
}

interface ModuleContextValue {
  modules: Module[]
  registerModule: (module: Module) => boolean
  unregisterModule: (moduleId: string) => boolean
  enableModule: (moduleId: string) => void
  disableModule: (moduleId: string) => void
  isModuleEnabled: (moduleId: string) => boolean
}

const ModuleContext = createContext<ModuleContextValue | undefined>(undefined)

export const ModuleProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [modules, setModules] = useState<Module[]>([])

  const registerModule = useCallback((module: Module): boolean => {
    if (modules.some(m => m.id === module.id)) {
      console.warn(`[ModuleSystem] Module ${module.id} already registered`)
      return false
    }
    setModules(prev => [...prev, module])
    console.log(`[ModuleSystem] Module registered: ${module.name} v${module.version}`)
    return true
  }, [modules])

  const unregisterModule = useCallback((moduleId: string): boolean => {
    const existed = modules.some(m => m.id === moduleId)
    if (!existed) {
      console.warn(`[ModuleSystem] Module ${moduleId} not found`)
      return false
    }
    setModules(prev => prev.filter(m => m.id !== moduleId))
    console.log(`[ModuleSystem] Module unregistered: ${moduleId}`)
    return true
  }, [modules])

  const enableModule = useCallback((moduleId: string): void => {
    setModules(prev => prev.map(m =>
      m.id === moduleId ? { ...m, enabled: true } : m
    ))
  }, [])

  const disableModule = useCallback((moduleId: string): void => {
    setModules(prev => prev.map(m =>
      m.id === moduleId ? { ...m, enabled: false } : m
    ))
  }, [])

  const isModuleEnabled = useCallback((moduleId: string): boolean => {
    const module = modules.find(m => m.id === moduleId)
    return module?.enabled ?? false
  }, [modules])

  const value: ModuleContextValue = {
    modules,
    registerModule,
    unregisterModule,
    enableModule,
    disableModule,
    isModuleEnabled,
  }

  return (
    <ModuleContext.Provider value={value}>
      {children}
    </ModuleContext.Provider>
  )
}

export const useModuleSystem = (): ModuleContextValue => {
  const context = useContext(ModuleContext)
  if (!context) {
    throw new Error('useModuleSystem must be used within a ModuleProvider')
  }
  return context
}

export const createModuleAPI = (): ModuleAPI => ({
  registerModule: () => false,
  unregisterModule: () => false,
  enableModule: () => {},
  disableModule: () => {},
  getModule: () => undefined,
  getAllModules: () => [],
  getEnabledModules: () => [],
})

export default ModuleProvider