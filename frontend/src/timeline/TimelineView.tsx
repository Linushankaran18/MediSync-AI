import type { TimelineEvent } from '../api/client';

const icons: Record<string, string> = {
  visit: '🏥',
  medication: '💊',
  lab_result: '🧪',
  doctor_note: '📝',
};

export default function TimelineView({ events }: { events: TimelineEvent[] }) {
  if (!events.length) {
    return <p className="text-slate-500">No timeline events yet. Upload documents to build your timeline.</p>;
  }

  return (
    <div className="relative">
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200" />
      <div className="space-y-6">
        {events.map((event) => (
          <div key={event.id} className="relative pl-10">
            <div className="absolute left-2 w-5 h-5 rounded-full bg-blue-100 border-2 border-blue-500 flex items-center justify-center text-xs">
              {icons[event.event_type]?.[0] || '•'}
            </div>
            <div className="bg-white rounded-xl border p-4">
              <div className="flex justify-between items-start">
                <p className="font-semibold capitalize">{event.event_type.replace('_', ' ')}</p>
                <span className="text-sm text-slate-500">{event.event_date || 'Unknown date'}</span>
              </div>
              {event.payload && (
                <pre className="mt-2 text-sm text-slate-600 whitespace-pre-wrap">
                  {JSON.stringify(event.payload, null, 2)}
                </pre>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
