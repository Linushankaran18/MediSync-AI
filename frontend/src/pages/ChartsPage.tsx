import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import LabChart from '../charts/LabChart';
import { dataApi } from '../api/client';

const tests = [
  { key: 'blood_sugar', label: 'Blood Sugar' },
  { key: 'blood_pressure', label: 'Blood Pressure' },
  { key: 'cholesterol', label: 'Cholesterol' },
  { key: 'creatinine', label: 'Creatinine' },
];

export default function ChartsPage() {
  const [selected, setSelected] = useState('blood_sugar');
  const { data: trend } = useQuery({
    queryKey: ['lab-trends', selected],
    queryFn: () => dataApi.labTrends(selected).then((r) => r.data),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Lab Trends</h1>
      <div className="flex gap-2 mb-6 flex-wrap">
        {tests.map((t) => (
          <button
            key={t.key}
            onClick={() => setSelected(t.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              selected === t.key ? 'bg-blue-600 text-white' : 'bg-white border text-slate-600'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      {trend && (
        <div className="bg-white rounded-xl border p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold">{trend.test_name}</h2>
            <span className="text-sm capitalize px-2 py-1 bg-slate-100 rounded">{trend.trend}</span>
          </div>
          <LabChart points={trend.points} />
        </div>
      )}
    </div>
  );
}
