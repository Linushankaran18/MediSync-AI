import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import TimelineView from '../timeline/TimelineView';
import { dataApi } from '../api/client';

export default function TimelinePage() {
  const { data: events, isLoading } = useQuery({
    queryKey: ['timeline'],
    queryFn: () => dataApi.timeline().then((r) => r.data),
  });

  if (isLoading) return <p className="text-slate-500">Loading timeline...</p>;

  if (!events?.length) {
    return (
      <div className="text-center py-16">
        <h1 className="text-2xl font-bold mb-2">Medical Timeline</h1>
        <p className="text-slate-500 mb-6">
          No events yet. Upload a document to start building the patient's timeline.
        </p>
        <Link to="/upload" className="text-blue-600 font-medium hover:underline">
          Go to Upload →
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Medical Timeline</h1>
      <TimelineView events={events} />
    </div>
  );
}
