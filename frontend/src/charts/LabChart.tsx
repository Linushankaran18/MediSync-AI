import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { LabTrendPoint } from '../api/client';

export default function LabChart({ points }: { points: LabTrendPoint[] }) {
  if (!points.length) {
    return <p className="text-slate-500 text-sm">No data points available for this test.</p>;
  }

  const data = points.map((p) => ({
    date: p.date || 'N/A',
    value: p.value,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} dot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
