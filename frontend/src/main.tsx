import React, { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([])
  const [loading, setLoading] = useState(false)

  const send = async () => {
    if (!input.trim()) return
    const next = [...messages, { role: 'user', content: input }]
    setMessages(next)
    setInput('')
    setLoading(true)

    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: next, stream: true })
    })

    if (!res.ok) {
      setLoading(false)
      alert('Request failed')
      return
    }

    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let assistant = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      for (const line of chunk.split('\n')) {
        if (line.startsWith('data: ')) {
          try {
            const evt = JSON.parse(line.slice(6))
            if (evt.done) {
              setMessages(m => [...m, { role: 'assistant', content: assistant }])
              assistant = ''
              setLoading(false)
              return
            } else {
              assistant += evt.content
            }
          } catch {}
        }
      }
    }

    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 720, margin: '40px auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1>LangChain Chatbot</h1>
      <div style={{ padding: 12, border: '1px solid #ddd', borderRadius: 8, minHeight: 200 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ whiteSpace: 'pre-wrap', margin: '8px 0' }}>
            <b>{m.role === 'user' ? 'You' : 'Assistant'}:</b> {m.content}
          </div>
        ))}
        {loading && <div>Thinking…</div>}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask anything" style={{ flex: 1, padding: 8 }} />
        <button onClick={send} disabled={loading}>Send</button>
      </div>
    </div>
  )
}

createRoot(document.getElementById('root')!).render(<App />)
