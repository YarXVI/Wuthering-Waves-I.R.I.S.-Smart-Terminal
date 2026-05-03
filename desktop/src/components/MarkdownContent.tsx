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
