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
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Props {
  content: string
}

function CodeBlock({ className, children }: { className?: string; children?: React.ReactNode }) {
  const match = /language-(\w+)/.exec(className || '')
  const lang = match ? match[1] : ''
  return (
    <pre className="md-code-block">
      {lang && <div className="md-code-lang">{lang}</div>}
      <code className={className}>{String(children).replace(/\n$/, '')}</code>
    </pre>
  )
}

const MarkdownContent: React.FC<Props> = ({ content }) => {
  return (
    <div className="md-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className, children, ...props }) {
            const isInline = !className
            if (isInline) {
              return <code className="md-inline-code" {...props}>{children}</code>
            }
            return <CodeBlock className={className}>{children}</CodeBlock>
          },
          a({ href, children }) {
            return <a className="md-link" href={href} target="_blank" rel="noopener noreferrer">{children}</a>
          },
          table({ children }) {
            return <div className="md-table-wrap"><table className="md-table">{children}</table></div>
          },
          blockquote({ children }) {
            return <blockquote className="md-blockquote">{children}</blockquote>
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default MarkdownContent
