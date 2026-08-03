import { useState } from 'react';
import ConfidenceBadge from '../components/ConfidenceBadge';
import EvidencePanel from '../components/EvidencePanel';
import { dataApi, type ChatResponse } from '../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  response?: ChatResponse;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);
    try {
      const { data } = await dataApi.chat(question);
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer, response: data }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, I could not process your question. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border flex flex-col h-[600px]">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-slate-400 text-sm text-center mt-8">
            Try: &quot;Why did my doctor change my medicine?&quot; or &quot;What were my latest lab results?&quot;
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-xl p-4 ${
              m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-50 border'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{m.content}</p>
              {m.response && (
                <>
                  <div className="mt-2">
                    <ConfidenceBadge confidence={m.response.confidence} />
                  </div>
                  <EvidencePanel evidence={m.response.evidence} />
                  <p className="mt-2 text-xs text-slate-500 italic">{m.response.disclaimer}</p>
                </>
              )}
            </div>
          </div>
        ))}
        {loading && <p className="text-sm text-slate-400">Thinking...</p>}
      </div>
      <div className="border-t p-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask about your medical documents..."
          className="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={send}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
