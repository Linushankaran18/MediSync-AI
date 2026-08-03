import type { Alert } from '../api/client';

const severityStyles: Record<string, { badge: string; border: string; icon: string }> = {
  critical: { badge: 'bg-red-100 text-red-700', border: 'border-l-red-500 bg-red-50', icon: '⛔' },
  major: { badge: 'bg-orange-100 text-orange-700', border: 'border-l-orange-500 bg-orange-50', icon: '⚠️' },
  warning: { badge: 'bg-yellow-100 text-yellow-800', border: 'border-l-yellow-500 bg-yellow-50', icon: '⚠️' },
  minor: { badge: 'bg-blue-100 text-blue-700', border: 'border-l-blue-500 bg-blue-50', icon: 'ℹ️' },
  info: { badge: 'bg-slate-100 text-slate-700', border: 'border-l-slate-400 bg-slate-50', icon: 'ℹ️' },
};

const typeLabels: Record<string, string> = {
  drug_interaction: 'Drug Interaction',
  allergy: 'Allergy Alert',
  duplicate_prescription: 'Duplicate Prescription',
  dosage_conflict: 'Dosage Conflict',
  lab_trend: 'Lab Trend',
};

function AlertTags({ details }: { details: Record<string, unknown> }) {
  const tags = [details.medication_a, details.medication_b, details.medication, details.allergen, details.test_name].filter(
    (v): v is string => typeof v === 'string',
  );
  const uniqueTags = Array.from(new Set(tags));
  if (!uniqueTags.length) return null;
  return (
    <div className="flex gap-2 mt-2 flex-wrap">
      {uniqueTags.map((t) => (
        <span key={t} className="text-xs font-medium bg-white/80 border border-current/20 rounded-full px-2 py-0.5">
          {t}
        </span>
      ))}
    </div>
  );
}

export default function AlertCard({ alert }: { alert: Alert }) {
  const style = severityStyles[alert.severity] || severityStyles.info;
  const details = (alert.details ?? {}) as Record<string, unknown>;
  const description = typeof details.description === 'string' ? details.description : null;

  return (
    <div className={`rounded-lg border-l-4 border p-4 ${style.border}`}>
      <div className="flex items-start gap-3">
        <span className="text-lg leading-none" aria-hidden="true">{style.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <p className="font-semibold text-slate-900">{typeLabels[alert.alert_type] || alert.alert_type}</p>
            <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded-full shrink-0 ${style.badge}`}>
              {alert.severity}
            </span>
          </div>
          {description && <p className="text-sm text-slate-700 mt-1">{description}</p>}
          <AlertTags details={details} />
          <p className="text-xs text-slate-500 mt-2">
            This is not a diagnosis - please confirm with a doctor or pharmacist.
          </p>
        </div>
      </div>
    </div>
  );
}
