import { useQuery } from '@tanstack/react-query';
import AlertCard from '../components/AlertCard';
import { dataApi } from '../api/client';

export default function DashboardPage() {
  const { data: summary } = useQuery({ queryKey: ['summary'], queryFn: () => dataApi.summary().then((r) => r.data) });
  const { data: alerts } = useQuery({ queryKey: ['alerts'], queryFn: () => dataApi.alerts().then((r) => r.data) });
  const { data: documents } = useQuery({ queryKey: ['documents'], queryFn: () => dataApi.documents().then((r) => r.data) });

  const stats = [
    { label: 'Documents', value: summary?.document_count ?? 0 },
    { label: 'Visits', value: summary?.visit_count ?? 0 },
    { label: 'Medications', value: summary?.medication_count ?? 0 },
    { label: 'Active Alerts', value: summary?.active_alerts ?? 0, highlight: true },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-xl border p-4">
            <p className="text-sm text-slate-500">{s.label}</p>
            <p className={`text-2xl font-bold ${s.highlight && s.value > 0 ? 'text-red-600' : 'text-slate-900'}`}>
              {s.value}
            </p>
          </div>
        ))}
      </div>

      {alerts && alerts.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Safety Alerts</h2>
          <div className="grid gap-3">
            {alerts.map((a) => <AlertCard key={a.id} alert={a} />)}
          </div>
        </section>
      )}

      <section>
        <h2 className="text-lg font-semibold mb-3">Recent Documents</h2>
        <div className="bg-white rounded-xl border divide-y">
          {documents?.length ? documents.slice(0, 5).map((d) => (
            <div key={d.id} className="p-4 flex justify-between items-center">
              <div>
                <p className="font-medium">{d.filename}</p>
                <p className="text-sm text-slate-500">{d.doc_type}</p>
              </div>
              <span className="text-xs text-slate-400">
                OCR: {(d.ocr_quality * 100).toFixed(0)}%
              </span>
            </div>
          )) : (
            <p className="p-4 text-slate-500 text-sm">No documents uploaded yet.</p>
          )}
        </div>
      </section>
    </div>
  );
}
