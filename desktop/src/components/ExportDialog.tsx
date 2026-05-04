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

interface ExportDialogProps {
  content: string
  onClose: () => void
  onCopy: () => void
  onDownload: () => void
}

export default function ExportDialog({ content, onClose, onCopy, onDownload }: ExportDialogProps) {
  return (
    <div className="dialog" style={{ width: '95%', maxWidth: 700, maxHeight: '85vh', overflowY: 'auto' }}>
      <div className="dialog-title">Export Meeting</div>
      <pre
        style={{
          background: 'var(--nb-bg-secondary)',
          border: '1px solid var(--nb-border)',
          borderRadius: 8,
          padding: 12,
          fontSize: 12,
          lineHeight: 1.5,
          maxHeight: '50vh',
          overflowY: 'auto',
          color: 'var(--nb-text-primary)',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          marginBottom: 12,
        }}
      >
        {content}
      </pre>
      <div className="dialog-actions" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="dialog-btn-cancel" onClick={onCopy}>Copy</button>
          <button className="dialog-btn-confirm" onClick={onDownload}>Download</button>
        </div>
        <button className="dialog-btn-cancel" onClick={onClose}>Close</button>
      </div>
    </div>
  )
}
