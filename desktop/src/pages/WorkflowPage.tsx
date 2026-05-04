import React, { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

interface WorkflowAgent {
  id: string
  name: string
  title: string
  status: string
}

interface WorkflowStep {
  agent_id: string
  task: string
  result?: string
}

interface SavedWorkflow {
  id: string
  name: string
  step_count: number
  created_at: string
  updated_at: string
}

const WorkflowPage: React.FC = () => {
  const { t } = useLanguage()
  const [agents, setAgents] = useState<WorkflowAgent[]>([])
  const [steps, setSteps] = useState<WorkflowStep[]>([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [taskInput, setTaskInput] = useState('')
  const [running, setRunning] = useState(false)
  const [executingStep, setExecutingStep] = useState(-1)
  const [workflowName, setWorkflowName] = useState('')
  const [currentWorkflowId, setCurrentWorkflowId] = useState<string | null>(null)
  const [savedWorkflows, setSavedWorkflows] = useState<SavedWorkflow[]>([])
  const [showLoadDialog, setShowLoadDialog] = useState(false)

  useEffect(() => {
    loadAgents()
    loadSavedWorkflows()
  }, [])

  async function loadAgents() {
    try {
      const res = await (window as any).agentAPI.listCollaborationAgents()
      setAgents(res.agents || [])
    } catch {}
  }

  async function loadSavedWorkflows() {
    try {
      const res = await (window as any).agentAPI.listWorkflows()
      setSavedWorkflows(res.workflows || [])
    } catch {}
  }

  function addStep() {
    if (!selectedAgent || !taskInput.trim()) return
    setSteps([...steps, { agent_id: selectedAgent, task: taskInput.trim() }])
    setTaskInput('')
  }

  function removeStep(idx: number) {
    setSteps(steps.filter((_, i) => i !== idx))
  }

  async function executeWorkflow() {
    if (steps.length === 0) return
    setRunning(true)
    const results: WorkflowStep[] = []

    for (let i = 0; i < steps.length; i++) {
      setExecutingStep(i)
      const step = steps[i]
      try {
        const res = await (window as any).agentAPI.callAgent(step.agent_id, step.task)
        results.push({ ...step, result: res.reply || res.error || 'No response' })
      } catch (e: any) {
        results.push({ ...step, result: `Error: ${e.message}` })
      }
      setSteps([...results])
    }

    setExecutingStep(-1)
    setRunning(false)
  }

  function clearWorkflow() {
    setSteps([])
    setWorkflowName('')
    setCurrentWorkflowId(null)
  }

  async function saveWorkflow() {
    if (!workflowName.trim() || steps.length === 0) return
    try {
      const workflow = {
        id: currentWorkflowId || undefined,
        name: workflowName.trim(),
        steps: steps.map(s => ({ agent_id: s.agent_id, task: s.task, result: s.result || null })),
      }
      const res = await (window as any).agentAPI.saveWorkflow(workflow)
      if (res.workflow?.id) {
        setCurrentWorkflowId(res.workflow.id)
        loadSavedWorkflows()
      }
    } catch {}
  }

  async function loadWorkflow(workflowId: string) {
    try {
      const res = await (window as any).agentAPI.getWorkflow(workflowId)
      if (res.workflow) {
        const w = res.workflow
        setSteps(w.steps || [])
        setWorkflowName(w.name || '')
        setCurrentWorkflowId(w.id || null)
        setShowLoadDialog(false)
      }
    } catch {}
  }

  async function deleteWorkflow(workflowId: string, e: React.MouseEvent) {
    e.stopPropagation()
    if (!confirm('Delete this workflow?')) return
    try {
      await (window as any).agentAPI.deleteWorkflow(workflowId)
      if (currentWorkflowId === workflowId) {
        clearWorkflow()
      }
      loadSavedWorkflows()
    } catch {}
  }

  return (
    <div style={{ padding: 'var(--nb-space-lg)', maxWidth: 900, margin: '0 auto', height: '100%', overflowY: 'auto' }}>
      <div style={{ marginBottom: 'var(--nb-space-xl)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 className="nb-text-lg nb-font-semibold" style={{ margin: 0 }}>{t.workflow.orchestration}</h2>
          <p className="nb-text-sm nb-text-tertiary" style={{ margin: 'var(--nb-space-xs) 0 0' }}>
            {t.workflow.description}
          </p>
        </div>
        <button
          onClick={() => setShowLoadDialog(true)}
          className="nb-btn nb-btn-secondary nb-btn-sm"
        >
          馃搨 {t.workflow.loadWorkflow}
        </button>
      </div>

      {/* Load Dialog */}
      {showLoadDialog && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000
        }}
          onClick={() => setShowLoadDialog(false)}
        >
          <div className="nb-card" style={{ width: 400, maxWidth: '90vw' }} onClick={e => e.stopPropagation()}>
            <div className="nb-text-base nb-font-semibold" style={{ marginBottom: 'var(--nb-space-md)' }}>
              Saved Workflows ({savedWorkflows.length})
            </div>
            {savedWorkflows.length === 0 ? (
              <div className="nb-text-sm nb-text-muted" style={{ textAlign: 'center', padding: 'var(--nb-space-xl)' }}>
                No saved workflows yet
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nb-space-sm)', maxHeight: 300, overflowY: 'auto' }}>
                {savedWorkflows.map(w => (
                  <div key={w.id} className="nb-card" style={{ cursor: 'pointer' }}
                    onClick={() => loadWorkflow(w.id)}
                  >
                    <div style={{ flex: 1 }}>
                      <div className="nb-text-sm nb-font-medium">{w.name}</div>
                      <div className="nb-text-xs nb-text-muted" style={{ marginTop: 'var(--nb-space-xs)' }}>
                        {w.step_count} steps 路 {w.updated_at ? new Date(w.updated_at).toLocaleDateString() : 'N/A'}
                      </div>
                    </div>
                    <button
                      onClick={(e) => deleteWorkflow(w.id, e)}
                      className="nb-btn nb-btn-danger nb-btn-sm nb-btn-icon"
                    >脳</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Workflow Name */}
      <div className="nb-card" style={{ marginBottom: 'var(--nb-space-lg)' }}>
        <div className="nb-text-sm nb-font-medium" style={{ marginBottom: 'var(--nb-space-md)' }}>
          {t.workflow.workflowName}
        </div>
        <div style={{ display: 'flex', gap: 'var(--nb-space-sm)' }}>
          <input
            type="text"
            placeholder={t.workflow.untitled}
            value={workflowName}
            onChange={e => setWorkflowName(e.target.value)}
            className="nb-input"
          />
          <button
            onClick={saveWorkflow}
            disabled={!workflowName.trim() || steps.length === 0}
            className="nb-btn nb-btn-primary nb-btn-sm"
          >
            馃捑 {t.workflow.save}
          </button>
        </div>
        {currentWorkflowId && (
          <div className="nb-text-xs nb-text-muted" style={{ marginTop: 'var(--nb-space-sm)' }}>
            Workflow ID: {currentWorkflowId}
          </div>
        )}
      </div>

      {/* Agent Selection */}
      <div className="nb-card" style={{ marginBottom: 'var(--nb-space-lg)' }}>
        <div className="nb-text-sm nb-font-medium" style={{ marginBottom: 'var(--nb-space-md)' }}>
          {t.workflow.addStep}
        </div>
        <div style={{ display: 'flex', gap: 'var(--nb-space-sm)', flexWrap: 'wrap' }}>
          <select
            value={selectedAgent}
            onChange={e => setSelectedAgent(e.target.value)}
            className="nb-input nb-select"
            style={{ flex: 1, minWidth: 150 }}
          >
            <option value="">{t.workflow.selectAgent}</option>
            {agents.map(a => (
              <option key={a.id} value={a.id}>{a.name} 鈥?{a.title}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder={t.workflow.taskDescription}
            value={taskInput}
            onChange={e => setTaskInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addStep() } }}
            className="nb-input"
            style={{ flex: 2, minWidth: 200 }}
          />
          <button
            onClick={addStep}
            disabled={!selectedAgent || !taskInput.trim()}
            className="nb-btn nb-btn-secondary nb-btn-sm"
          >{t.workflow.add}</button>
        </div>
      </div>

      {/* Workflow Steps */}
      {steps.length > 0 && (
        <div className="nb-card" style={{ marginBottom: 'var(--nb-space-lg)' }}>
          <div className="nb-text-sm nb-font-medium" style={{ marginBottom: 'var(--nb-space-md)' }}>
            Workflow Steps ({steps.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nb-space-sm)' }}>
            {steps.map((step, idx) => {
              const agent = agents.find(a => a.id === step.agent_id)
              return (
                <div key={idx} className="nb-card" style={{
                  borderColor: executingStep === idx ? 'var(--nb-info)' : undefined,
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--nb-space-md)' }}>
                    <div style={{
                      width: 28, height: 28, borderRadius: '50%',
                      background: step.result ? (step.result.startsWith('Error') ? 'var(--nb-error-bg)' : 'var(--nb-success-bg)') : 'var(--nb-bg-tertiary)',
                      color: step.result ? (step.result.startsWith('Error') ? 'var(--nb-error)' : 'var(--nb-success)') : 'var(--nb-text-muted)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 12, fontWeight: 500, flexShrink: 0
                    }}>
                      {executingStep === idx ? '⏳' : (step.result ? (step.result.startsWith('Error') ? '✗' : '✓') : idx + 1)}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div className="nb-text-xs nb-text-tertiary" style={{ marginBottom: 'var(--nb-space-xs)' }}>
                        {agent?.name || step.agent_id}
                      </div>
                      <div className="nb-text-sm">{step.task}</div>
                      {step.result && (
                        <div className="nb-card" style={{
                          marginTop: 'var(--nb-space-sm)',
                          color: step.result.startsWith('Error') ? 'var(--nb-error)' : undefined,
                          maxHeight: 150, overflowY: 'auto'
                        }}>
                          {step.result}
                        </div>
                      )}
                    </div>
                    {!running && (
                      <button
                        onClick={() => removeStep(idx)}
                        className="nb-btn nb-btn-danger nb-btn-sm nb-btn-icon"
                      >脳</button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 'var(--nb-space-sm)' }}>
        <button
          onClick={executeWorkflow}
          disabled={steps.length === 0 || running}
          className="nb-btn nb-btn-primary"
        >
          {running ? `鈴?Running step ${executingStep + 1}...` : `鈻?${t.workflow.execute}`}
        </button>
        <button
          onClick={clearWorkflow}
          disabled={running || steps.length === 0}
          className="nb-btn nb-btn-secondary"
        >
          {t.workflow.clear}
        </button>
      </div>
    </div>
  )
}

export default WorkflowPage