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





import React, { useState, useEffect } from 'react'





interface KanbanTask {


  entry_id: string


  room_id: string


  author: string


  content: string


  resolved: boolean


}





interface KanbanBoardProps {


  activeId: string | null


  onClose?: () => void


}





export default function KanbanBoard({ activeId, onClose }: KanbanBoardProps) {


  const [tasks, setTasks] = useState<KanbanTask[]>([])


  const [filter, setFilter] = useState<'all' | 'open' | 'done'>('all')





  useEffect(() => {


    loadKanban(filter)


  }, [activeId])





  async function loadKanban(f: 'all' | 'open' | 'done') {


    try {


      const res = await fetch('http://127.0.0.1:8000/whiteboard/entries?type=task')


      const data = await res.json()


      let entries: KanbanTask[] = data.entries || []


      if (f === 'open') entries = entries.filter(e => !e.resolved)


      if (f === 'done') entries = entries.filter(e => e.resolved)


      if (activeId) entries = entries.filter(e => e.room_id === activeId)


      setTasks(entries)


    } catch {}


  }





  async function resolveTask(roomId: string, entryId: string) {


    try {


      await fetch(`http://127.0.0.1:8000/whiteboard/entries/${entryId}/resolve`, {


        method: 'POST',


        headers: { 'Content-Type': 'application/json' },


        body: JSON.stringify({ resolved: true }),


      })


      loadKanban(filter)


    } catch {}


  }





  return (


    <div className="dialog" style={{ width: '95%', maxWidth: 800, maxHeight: '85vh', overflowY: 'auto' }}>


      <div className="dialog-title">Task Kanban</div>


      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>


        {(['all', 'open', 'done'] as const).map(f => (


          <button


            style={{


              padding: '4px 12px',


              borderRadius: 6,


              fontSize: 11,


              background: filter === f ? 'var(--nb-bg-tertiary)' : 'transparent',


              color: filter === f ? 'var(--nb-text-primary)' : 'var(--nb-text-muted)',


              border: '1px solid var(--nb-border-strong)',


              cursor: 'pointer',


              textTransform: 'capitalize',


            }}


            onClick={() => { setFilter(f); loadKanban(f) }}


          >


            {f}


          </button>


        ))}


      </div>


      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>


        {tasks.length === 0 && (


          <div style={{ gridColumn: '1/-1', textAlign: 'center', color: 'var(--nb-text-muted)', fontSize: 12, padding: 20 }}>


            No tasks found


          </div>


        )}


        {tasks.map(task => (


          <div


            key={task.entry_id}


            style={{


              background: 'var(--nb-bg-secondary)',


              border: '1px solid var(--nb-border)',


              borderRadius: 8,


              padding: 10,


              fontSize: 12,


            }}


          >


            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>


              <span


                style={{


                  fontSize: 10,


                  padding: '2px 6px',


                  borderRadius: 4,


                  background: task.resolved ? 'rgba(16,185,129,0.15)' : 'rgba(59,130,246,0.15)',


                  color: task.resolved ? '#10b981' : '#3b82f6',


                }}


              >


                {task.resolved ? 'Done' : 'Open'}


              </span>


              <span style={{ fontSize: 10, color: 'var(--nb-text-muted)' }}>


                {task.room_id.replace('meeting_', '').replace(/_/g, '-')}


              </span>


            </div>


            <div style={{ color: 'var(--nb-text-primary)', marginBottom: 6, lineHeight: 1.4 }}>{task.content}</div>


            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>


              <span style={{ fontSize: 10, color: 'var(--nb-text-muted)' }}>{task.author}</span>


              {!task.resolved && (


                <button


                  style={{


                    fontSize: 10,


                    padding: '2px 8px',


                    borderRadius: 4,


                    border: '1px solid rgba(16,185,129,0.3)',


                    background: 'transparent',


                    color: '#10b981',


                    cursor: 'pointer',


                  }}


                  onClick={() => resolveTask(task.room_id, task.entry_id)}


                >


                  Done


                </button>


              )}


            </div>


          </div>


        ))}


      </div>


      <div className="dialog-actions" style={{ justifyContent: 'flex-end', marginTop: 12 }}>


        {onClose && <button className="dialog-btn-cancel" onClick={onClose}>Close</button>}


      </div>


    </div>


  )


}


