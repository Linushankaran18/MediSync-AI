import ChatInterface from '../chat/ChatInterface';

export default function ChatPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">AI Medical Assistant</h1>
      <p className="text-slate-500 mb-6">Ask questions about your medical documents. Answers include evidence and confidence scores.</p>
      <ChatInterface />
    </div>
  );
}
