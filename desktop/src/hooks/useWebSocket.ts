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

import { useEffect, useRef, useState, useCallback } from 'react'

export type WsStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting'

export interface UseWebSocketOptions {
  url: string | null
  onMessage?: (data: any) => void
  onOpen?: () => void
  onClose?: () => void
  maxReconnectAttempts?: number
  debugName?: string
}

export interface UseWebSocketReturn {
  status: WsStatus
  send: (data: any) => void
  disconnect: () => void
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  maxReconnectAttempts = 10,
  debugName = 'unknown',
}: UseWebSocketOptions): UseWebSocketReturn {
  const [status, setStatus] = useState<WsStatus>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptRef = useRef(0)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const urlRef = useRef(url)

  useEffect(() => {
    urlRef.current = url
  }, [url])

  const connect = useCallback(() => {
    if (!urlRef.current) return

    if (wsRef.current) {
      wsRef.current.onclose = null
      wsRef.current.close()
    }

    setStatus('reconnecting')
    console.log(`[WS][${debugName}] connecting to:`, urlRef.current)
    const ws = new WebSocket(urlRef.current)
    wsRef.current = ws

    ws.onopen = () => {
      console.log(`[WS][${debugName}] connected:`, urlRef.current)
      setStatus('connected')
      reconnectAttemptRef.current = 0
      onOpen?.()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch {
        onMessage?.(event.data)
      }
    }

    ws.onerror = () => {
      console.warn(`[WS][${debugName}] error:`, urlRef.current)
    }

    ws.onclose = () => {
      console.log(`[WS][${debugName}] closed:`, urlRef.current)
      setStatus('reconnecting')
      if (reconnectAttemptRef.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(1.5, reconnectAttemptRef.current), 30000)
        reconnectAttemptRef.current++
        console.log(`[WS][${debugName}] reconnect in ${delay}ms (attempt ${reconnectAttemptRef.current})`)
        reconnectTimerRef.current = setTimeout(() => {
          if (wsRef.current === ws) connect()
        }, delay)
      } else {
        console.error(`[WS][${debugName}] max reconnect attempts reached`)
        setStatus('disconnected')
        onClose?.()
      }
    }
  }, [debugName, maxReconnectAttempts])

  useEffect(() => {
    if (!url) {
      setStatus('disconnected')
      return
    }
    setStatus('connecting')
    connect()
    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      if (wsRef.current) {
        wsRef.current.onclose = null
        wsRef.current.close()
      }
      wsRef.current = null
      setStatus('disconnected')
    }
  }, [url, connect])

  const send = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }, [])

  const disconnect = useCallback(() => {
    reconnectAttemptRef.current = maxReconnectAttempts
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
    if (wsRef.current) {
      wsRef.current.onclose = null
      wsRef.current.close()
    }
    wsRef.current = null
    setStatus('disconnected')
  }, [maxReconnectAttempts])

  return { status, send, disconnect }
}