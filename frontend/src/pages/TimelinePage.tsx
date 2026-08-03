import { useQuery } from '@tanstack/react-query';
import TimelineView from '../timeline/TimelineView';
import { dataApi } from '../api/client';

export default function TimelinePage() {
  const { data: events, isLoading } = useQuery({
    queryKey: ['timeline'],
    queryFn: () => dataApi.timeline().then((r) => r.data),
  });

  if (isLoading) return <p className="text-slate-500">Loading timeline...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Medical Timeline</h1>
      <TimelineView events={events || []} />
    </div>
  );
}
