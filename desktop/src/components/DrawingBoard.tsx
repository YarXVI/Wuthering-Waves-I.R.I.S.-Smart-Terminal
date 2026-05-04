import React, { useRef, useEffect, useState } from 'react'

interface DrawingBoardProps {
  width?: number
  height?: number
  onClose?: () => void
}

const DRAW_MODES = ['pen', 'eraser', 'line', 'arrow', 'rect', 'circle'] as const
type DrawMode = typeof DRAW_MODES[number]

export default function DrawingBoard({ width = 700, height = 400, onClose }: DrawingBoardProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const isDrawingRef = useRef(false)
  const lastPosRef = useRef<{ x: number; y: number } | null>(null)
  const startPosRef = useRef<{ x: number; y: number } | null>(null)
  const tempCanvasRef = useRef<HTMLCanvasElement | null>(null)

  const [drawColor, setDrawColor] = useState('#333333')
  const [drawSize, setDrawSize] = useState(3)
  const [drawMode, setDrawMode] = useState<DrawMode>('pen')

  function getCanvasPos(e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) {
    if (!canvasRef.current) return { x: 0, y: 0 }
    const rect = canvasRef.current.getBoundingClientRect()
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY
    return {
      x: (clientX - rect.left) * (canvasRef.current.width / rect.width),
      y: (clientY - rect.top) * (canvasRef.current.height / rect.height),
    }
  }

  function drawArrow(ctx: CanvasRenderingContext2D, fromX: number, fromY: number, toX: number, toY: number) {
    const headLen = 15
    const angle = Math.atan2(toY - fromY, toX - fromX)
    ctx.beginPath()
    ctx.moveTo(fromX, fromY)
    ctx.lineTo(toX, toY)
    ctx.lineTo(toX - headLen * Math.cos(angle - Math.PI / 6), toY - headLen * Math.sin(angle - Math.PI / 6))
    ctx.moveTo(toX, toY)
    ctx.lineTo(toX - headLen * Math.cos(angle + Math.PI / 6), toY - headLen * Math.sin(angle + Math.PI / 6))
    ctx.stroke()
  }

  function startDrawing(e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) {
    isDrawingRef.current = true
    const pos = getCanvasPos(e)
    lastPosRef.current = pos
    startPosRef.current = pos
    if (canvasRef.current && (drawMode === 'line' || drawMode === 'arrow' || drawMode === 'rect' || drawMode === 'circle')) {
      tempCanvasRef.current = document.createElement('canvas')
      tempCanvasRef.current.width = canvasRef.current.width
      tempCanvasRef.current.height = canvasRef.current.height
      const tempCtx = tempCanvasRef.current.getContext('2d')
      if (tempCtx && canvasRef.current) {
        tempCtx.drawImage(canvasRef.current, 0, 0)
      }
    }
  }

  function draw(e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) {
    if (!isDrawingRef.current || !canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return
    const pos = getCanvasPos(e)
    const last = lastPosRef.current
    const start = startPosRef.current
    if (!last) return

    const isShapeMode = drawMode === 'line' || drawMode === 'arrow' || drawMode === 'rect' || drawMode === 'circle'

    if (isShapeMode && tempCanvasRef.current) {
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
      ctx.drawImage(tempCanvasRef.current, 0, 0)
      ctx.strokeStyle = drawColor
      ctx.lineWidth = drawSize
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      if (drawMode === 'line') {
        ctx.beginPath()
        ctx.moveTo(start!.x, start!.y)
        ctx.lineTo(pos.x, pos.y)
        ctx.stroke()
      } else if (drawMode === 'arrow') {
        drawArrow(ctx, start!.x, start!.y, pos.x, pos.y)
      } else if (drawMode === 'rect') {
        ctx.beginPath()
        ctx.strokeRect(start!.x, start!.y, pos.x - start!.x, pos.y - start!.y)
      } else if (drawMode === 'circle') {
        const rx = Math.abs(pos.x - start!.x) / 2
        const ry = Math.abs(pos.y - start!.y) / 2
        const cx = start!.x + (pos.x - start!.x) / 2
        const cy = start!.y + (pos.y - start!.y) / 2
        ctx.beginPath()
        ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2)
        ctx.stroke()
      }
    } else {
      ctx.beginPath()
      ctx.moveTo(last.x, last.y)
      ctx.lineTo(pos.x, pos.y)
      ctx.strokeStyle = drawMode === 'eraser' ? '#ffffff' : drawColor
      ctx.lineWidth = drawSize
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      if (drawMode === 'eraser') {
        ctx.globalCompositeOperation = 'destination-out'
      } else {
        ctx.globalCompositeOperation = 'source-over'
      }
      ctx.stroke()
    }
    lastPosRef.current = pos
    if ('preventDefault' in e) e.preventDefault()
  }

  function stopDrawing() {
    isDrawingRef.current = false
    lastPosRef.current = null
    startPosRef.current = null
    tempCanvasRef.current = null
  }

  function clearCanvas() {
    if (!canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
  }

  function exportPng() {
    if (canvasRef.current) {
      const a = document.createElement('a')
      a.download = 'drawing.png'
      a.href = canvasRef.current.toDataURL('image/png')
      a.click()
    }
  }

  const modeButtons: { mode: DrawMode; icon: string }[] = [
    { mode: 'pen', icon: '✏️' },
    { mode: 'eraser', icon: '🧹' },
    { mode: 'line', icon: '📏' },
    { mode: 'arrow', icon: '➡️' },
    { mode: 'rect', icon: '⬜' },
    { mode: 'circle', icon: '⭕' },
  ]

  return (
    <div className="dialog" style={{ width: '95%', maxWidth: 750, maxHeight: '90vh', overflowY: 'auto' }}>
      <div className="dialog-title">Drawing Board</div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label style={{ fontSize: 11, color: 'var(--nb-text-muted)' }}>Color:</label>
          <input
            type="color"
            value={drawColor}
            onChange={e => setDrawColor(e.target.value)}
            style={{ width: 30, height: 30, border: '1px solid var(--nb-border-strong)', borderRadius: 4, cursor: 'pointer', padding: 0 }}
          />
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label style={{ fontSize: 11, color: 'var(--nb-text-muted)' }}>Size:</label>
          <input
            type="range"
            min={1}
            max={20}
            value={drawSize}
            onChange={e => setDrawSize(parseInt(e.target.value))}
            style={{ width: 100 }}
          />
          <span style={{ fontSize: 11, color: 'var(--nb-text-primary)', width: 20 }}>{drawSize}</span>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {modeButtons.map(({ mode, icon }) => (
            <button
              key={mode}
              style={{
                padding: '4px 8px',
                borderRadius: 6,
                fontSize: 11,
                background: drawMode === mode ? 'var(--nb-bg-tertiary)' : 'transparent',
                color: drawMode === mode ? 'var(--nb-text-primary)' : 'var(--nb-text-muted)',
                border: '1px solid var(--nb-border-strong)',
                cursor: 'pointer',
              }}
              onClick={() => setDrawMode(mode)}
            >
              {icon}
            </button>
          ))}
        </div>
        <button
          style={{ padding: '4px 10px', fontSize: 11, borderRadius: 6, border: '1px solid rgba(248,113,113,0.3)', background: 'transparent', cursor: 'pointer', color: '#f87171' }}
          onClick={clearCanvas}
        >
          Clear
        </button>
        <button
          style={{ padding: '4px 10px', fontSize: 11, borderRadius: 6, border: '1px solid var(--nb-border)', background: 'var(--nb-bg-tertiary)', cursor: 'pointer', color: 'var(--nb-accent)' }}
          onClick={exportPng}
        >
          馃摜 Export PNG
        </button>
        {onClose && (
          <button className="dialog-btn-cancel" onClick={onClose} style={{ marginLeft: 'auto' }}>
            Close
          </button>
        )}
      </div>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          background: '#ffffff',
          borderRadius: 8,
          border: '1px solid var(--nb-border)',
          cursor: 'crosshair',
          touchAction: 'none',
          display: 'block',
          maxWidth: '100%',
        }}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        onTouchStart={startDrawing}
        onTouchMove={draw}
        onTouchEnd={stopDrawing}
      />
    </div>
  )
}
