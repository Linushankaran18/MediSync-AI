import type { Alert } from '../api/client';

const severityColors: Record<string, string> = {
  critical: 'bg-red-50 border-red-200 text-red-800',
  major: 'bg-orange-50 border-orange-200 text-orange-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  minor: 'bg-blue-50 border-blue-200 text-blue-800',
  info: 'bg-slate-50 border-slate-200 text-slate-700',
};

const typeLabels: Record<string, string> = {
  drug_interaction: 'Drug Interaction',
  allergy: 'Allergy Alert',
  duplicate_prescription: 'Duplicate Prescription',
  dosage_conflict: 'Dosage Conflict',
  lab_trend: 'Lab Trend',
};

export default function AlertCard({ alert }: { alert: Alert }) {
  const color = severityColors[alert.severity] || severityColors.info;
  return (
    <div className={`rounded-lg border p-4 ${color}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="font-semibold">{typeLabels[alert.alert_type] || alert.alert_type}</p>
          <p className="text-xs uppercase mt-1 opacity-70">{alert.severity}</p>
        </div>
      </div>
      {alert.details && (
        <pre className="mt-2 text-xs whitespace-pre-wrap opacity-80">
          {JSON.stringify(alert.details, null, 2)}
        </pre>
      )}
    </div>
  );
}
