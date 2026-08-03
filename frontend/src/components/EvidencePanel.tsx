import type { EvidenceItem } from '../api/client';

export default function EvidencePanel({ evidence }: { evidence: EvidenceItem[] }) {
  if (!evidence.length) return null;
  return (
    <div className="mt-4 border-t pt-4">
      <h4 className="text-sm font-semibold text-slate-700 mb-2">Evidence</h4>
      <div className="space-y-2">
        {evidence.map((e, i) => (
          <div key={i} className="bg-slate-50 rounded p-3 text-sm">
            {e.visit_date && <p className="text-xs text-slate-500 mb-1">{e.visit_date}</p>}
            <p className="text-slate-700">{e.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
