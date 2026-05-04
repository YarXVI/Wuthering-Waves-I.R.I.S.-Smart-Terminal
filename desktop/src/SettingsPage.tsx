import React, { useState, useEffect } from 'react'


import AgentManager from './AgentManager'


import { useLanguage } from './contexts/LanguageContext'


import { Locale } from './locales'





// ---- Types ----





interface ProviderConfig {


  id: string


  name: string


  api_type: string


  api_key: string


  base_url: string


  model: string


  is_active: boolean


}





interface MCPConfig {


  id: string


  name: string


  command: string


  args: string[]


  env: Record<string, string>


  enabled: boolean


}





interface SkillInfo {


  name: string


  description: string


  enabled: boolean


  path: string


}





interface AgentSettingsInfo {


  id: string


  name: string


  provider_id: string


  system_prompt_override: string


  temperature: number


}





interface SettingsData {


  version: number


  providers: ProviderConfig[]


  mcp_servers: MCPConfig[]


  skill_bindings: { skill_name: string; agent_id: string; enabled: boolean }[]


  agent_settings: AgentSettingsInfo[]


  memrag_enabled: boolean


  theme: string


}





// ---- Tab Enum ----





type SettingsTab = 'general' | 'api' | 'mcp' | 'skills' | 'agents'





// ---- Props ----





interface SettingsPageProps {


  onClose: () => void


}





// ---- Component ----





const SettingsPage: React.FC<SettingsPageProps> = ({ onClose }) => {


  const [activeTab, setActiveTab] = useState<SettingsTab>('general')


  const [settings, setSettings] = useState<SettingsData | null>(null)


  const [skills, setSkills] = useState<SkillInfo[]>([])


  const [agents, setAgents] = useState<AgentSettingsInfo[]>([])


  const [saved, setSaved] = useState(false)


  const { locale, setLocale, t, localeNames } = useLanguage()





  useEffect(() => {


    loadSettings()


    loadSkills()


    loadAgents()


  }, [])





  async function loadSettings() {


    try {


      const res = await (window as any).agentAPI.getSettings()


      setSettings(res)


      if (res.agent_settings) {


        setAgents(res.agent_settings)


      }


    } catch {


      // Initialize settings with validated API configuration


      setSettings({


        version: 1,


        providers: [],


        mcp_servers: [],


        skill_bindings: [],


        agent_settings: [],


        memrag_enabled: false,


        theme: 'dark',


      })


    }


  }





  async function loadSkills() {


    try {


      const res = await (window as any).agentAPI.listSkills()


      setSkills(res.skills || [])


    } catch {}


  }





  async function loadAgents() {


    try {


      const res = await (window as any).agentAPI.listAgents()


      const agentList = (res.agents || []).map((a: any) => ({


        id: a.id,


        name: a.name,


        provider_id: '',


        system_prompt_override: '',


        temperature: 0.3,


      }))


      setAgents(prev => {


        const existing = new Map(prev.map(a => [a.id, a]))


        return agentList.map((a: any) => existing.get(a.id) || a)


      })


    } catch {}


  }





  async function saveProviders() {


    if (!settings) return


    try {


      await (window as any).agentAPI.updateProviders({ providers: settings.providers })


      showSaved()


    } catch {}


  }





  async function saveMCPServers() {


    if (!settings) return


    try {


      await (window as any).agentAPI.updateMCPServers({ servers: settings.mcp_servers })


      showSaved()


    } catch {}


  }





  async function toggleSkill(name: string, enabled: boolean) {


    try {


      await (window as any).agentAPI.toggleSkill(name, enabled)


      setSkills(prev => prev.map(s => s.name === name ? { ...s, enabled } : s))


    } catch {}


  }





  function showSaved() {


    setSaved(true)


    setTimeout(() => setSaved(false), 1500)


  }





  function updateProvider(index: number, field: keyof ProviderConfig, value: any) {


    if (!settings) return


    const providers = [...settings.providers]


    providers[index] = { ...providers[index], [field]: value }


    setSettings({ ...settings, providers })


  }





  function addProvider() {


    if (!settings) return


    const newProvider: ProviderConfig = {


      id: `provider_${Date.now()}`,


      name: 'New Provider',


      api_type: 'openai',


      api_key: '',


      base_url: 'https://api.openai.com/v1',


      model: 'gpt-4o',


      is_active: false,


    }


    setSettings({ ...settings, providers: [...settings.providers, newProvider] })


  }





  function removeProvider(index: number) {


    if (!settings) return


    const providers = settings.providers.filter((_, i) => i !== index)


    setSettings({ ...settings, providers })


  }





  function setActiveProvider(index: number) {


    if (!settings) return


    const providers = settings.providers.map((p, i) => ({


      ...p,


      is_active: i === index,


    }))


    setSettings({ ...settings, providers })


  }





  function updateMCP(index: number, field: keyof MCPConfig, value: any) {


    if (!settings) return


    const servers = [...settings.mcp_servers]


    servers[index] = { ...servers[index], [field]: value }


    setSettings({ ...settings, mcp_servers: servers })


  }





  function addMCP() {


    if (!settings) return


    const newServer: MCPConfig = {


      id: `mcp_${Date.now()}`,


      name: 'New MCP',


      command: '',


      args: [],


      env: {},


      enabled: false,


    }


    setSettings({ ...settings, mcp_servers: [...settings.mcp_servers, newServer] })


  }





  function removeMCP(index: number) {


    if (!settings) return


    const servers = settings.mcp_servers.filter((_, i) => i !== index)


    setSettings({ ...settings, mcp_servers: servers })


  }





  if (!settings) {


    return <div className="settings-page"><div className="settings-loading">{t.common.loading}</div></div>


  }





  return (


    <div className="settings-page">


      {/* Header */}


      <div className="settings-header">


        <h2>{t.settings.title}</h2>


        <div className="settings-header-actions">


          {saved && <span className="settings-saved-badge">✓ {t.settings.saved}</span>}


          <button className="settings-close-btn" onClick={onClose}>✗</button>


        </div>


      </div>





      {/* Tabs */}


      <div className="settings-tabs">


        <button


          className={`settings-tab ${activeTab === 'general' ? 'active' : ''}`}


          onClick={() => setActiveTab('general')}


        >


          {t.settings.title}


        </button>


        <button


          className={`settings-tab ${activeTab === 'api' ? 'active' : ''}`}


          onClick={() => setActiveTab('api')}


        >


          API {t.settings.providers}


        </button>


        <button


          className={`settings-tab ${activeTab === 'mcp' ? 'active' : ''}`}


          onClick={() => setActiveTab('mcp')}


        >


          MCP


        </button>


        <button


          className={`settings-tab ${activeTab === 'skills' ? 'active' : ''}`}


          onClick={() => setActiveTab('skills')}


        >


          {t.settings.skills}


        </button>


        <button


          className={`settings-tab ${activeTab === 'agents' ? 'active' : ''}`}


          onClick={() => setActiveTab('agents')}


        >


          {t.settings.agents}


        </button>


      </div>





      {/* Tab Content */}


      <div className="settings-content">


        {activeTab === 'general' && (


          <div className="settings-tab-content">


            <div className="settings-section">


              <h3>{t.settings.language}</h3>


              <div className="language-selector">


                {(Object.keys(localeNames) as Locale[]).map(loc => (


                  <button


                    key={loc}


                    className={`language-btn ${locale === loc ? 'active' : ''}`}


                    onClick={() => setLocale(loc)}


                  >


                    {localeNames[loc]}


                  </button>


                ))}


              </div>


            </div>


          </div>


        )}





        {activeTab === 'api' && (


          <div className="settings-tab-content">


            <p className="settings-desc">


              {t.settings.configureApi}


            </p>





            {settings.providers.map((provider, i) => (


              <div key={provider.id} className="provider-card">


                <div className="provider-header">


                  <input


                    className="provider-name-input"


                    value={provider.name}


                    onChange={e => updateProvider(i, 'name', e.target.value)}


                    placeholder={t.settings.providerName}


                  />


                  <div className="provider-actions">


                    <button


                      className={`btn-active ${provider.is_active ? 'on' : 'off'}`}


                      onClick={() => setActiveProvider(i)}


                    >


                      {provider.is_active ? t.settings.active : t.settings.setActive}


                    </button>


                    <button className="btn-remove" onClick={() => removeProvider(i)}>✗</button>


                  </div>


                </div>





                <div className="provider-fields">


                  <div className="field-row">


                    <label>{t.settings.type}</label>


                    <select


                      value={provider.api_type}


                      onChange={e => updateProvider(i, 'api_type', e.target.value)}


                    >


                      <option value="openai">OpenAI Compatible</option>


                      <option value="anthropic">Anthropic</option>


                      <option value="ollama">Ollama</option>


                    </select>


                  </div>


                  <div className="field-row">


                    <label>{t.settings.baseUrl}</label>


                    <input


                      value={provider.base_url}


                      onChange={e => updateProvider(i, 'base_url', e.target.value)}


                      placeholder="https://api.openai.com/v1"


                    />


                  </div>


                  <div className="field-row">


                    <label>{t.settings.apiKey}</label>


                    <input


                      type="password"


                      value={provider.api_key}


                      onChange={e => updateProvider(i, 'api_key', e.target.value)}


                      placeholder="sk-..."


                    />


                  </div>


                  <div className="field-row">


                    <label>{t.settings.model}</label>


                    <input


                      value={provider.model}


                      onChange={e => updateProvider(i, 'model', e.target.value)}


                      placeholder="gpt-4o"


                    />


                  </div>


                </div>


              </div>


            ))}





            <div className="settings-actions">


              <button className="btn-add" onClick={addProvider}>+ {t.settings.addProvider}</button>


              <button className="btn-save" onClick={saveProviders}>{t.settings.saveProviders}</button>


            </div>


          </div>


        )}





        {activeTab === 'mcp' && (


          <div className="settings-tab-content">


            <p className="settings-desc">


              {t.settings.mcpDesc}


            </p>





            {settings.mcp_servers.length === 0 && (


              <div className="empty-state">{t.settings.noMcpServers}</div>


            )}





            {settings.mcp_servers.map((server, i) => (


              <div key={server.id} className="mcp-card">


                <div className="provider-header">


                  <input


                    className="provider-name-input"


                    value={server.name}


                    onChange={e => updateMCP(i, 'name', e.target.value)}


                    placeholder={t.settings.mcpServerName}


                  />


                  <div className="provider-actions">


                    <button


                      className={`btn-active ${server.enabled ? 'on' : 'off'}`}


                      onClick={() => updateMCP(i, 'enabled', !server.enabled)}


                    >


                      {server.enabled ? t.settings.enabled : t.settings.disabled}


                    </button>


                    <button className="btn-remove" onClick={() => removeMCP(i)}>✗</button>


                  </div>


                </div>





                <div className="provider-fields">


                  <div className="field-row">


                    <label>{t.settings.command}</label>


                    <input


                      value={server.command}


                      onChange={e => updateMCP(i, 'command', e.target.value)}


                      placeholder="npx or python -m"


                    />


                  </div>


                  <div className="field-row">


                    <label>{t.settings.args}</label>


                    <input


                      value={server.args.join(' ')}


                      onChange={e => updateMCP(i, 'args', e.target.value.split(' ').filter(Boolean))}


                      placeholder="arg1 arg2"


                    />


                  </div>


                </div>


              </div>


            ))}





            <div className="settings-actions">


              <button className="btn-add" onClick={addMCP}>+ {t.settings.addMcpServer}</button>


              <button className="btn-save" onClick={saveMCPServers}>{t.settings.saveMcp}</button>


            </div>


          </div>


        )}





        {activeTab === 'skills' && (


          <div className="settings-tab-content">


            <p className="settings-desc">


              {t.settings.skillsDesc}


            </p>





            {skills.length === 0 && (


              <div className="empty-state">{t.settings.noSkills}</div>


            )}





            <div className="skills-list">


              {skills.map(skill => (


                <div key={skill.name} className="skill-card">


                  <div className="skill-info">


                    <span className="skill-name">{skill.name}</span>


                    <span className="skill-desc">{skill.description}</span>


                  </div>


                  <button


                    className={`btn-toggle ${skill.enabled ? 'on' : 'off'}`}


                    onClick={() => toggleSkill(skill.name, !skill.enabled)}


                  >


                    {skill.enabled ? t.settings.enabled : t.settings.disabled}


                  </button>


                </div>


              ))}


            </div>


          </div>


        )}





        {activeTab === 'agents' && (


          <div className="settings-tab-content">


            <AgentManager />


          </div>


        )}


      </div>


    </div>


  )


}





export default SettingsPage


