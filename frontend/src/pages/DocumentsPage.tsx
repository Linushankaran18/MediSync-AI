import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { dataApi, type Document } from '../api/client';

const docTypeStyles: Record<string, string> = {
  Prescription: 'bg-blue-100 text-blue-700',
  LabReport: 'bg-purple-100 text-purple-700',
  DoctorNote: 'bg-green-100 text-green-700',
  DischargeSummary: 'bg-orange-100 text-orange-700',
  Unknown: 'bg-slate-100 text-slate-700',
};

function DocumentRow({
  document,
  onDelete,
  isDeleting,
}: {
  document: Document;
  onDelete: (id: string) => void;
  isDeleting: boolean;
}) {
  const [confirming, setConfirming] = useState(false);

  return (
    <div className="p-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="min-w-0">
          <p className="font-medium text-slate-900 truncate">{document.filename}</p>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span
              className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                docTypeStyles[document.doc_type] || docTypeStyles.Unknown
              }`}
            >
              {document.doc_type || 'Unknown'}
            </span>
            <span className="text-xs text-slate-400">
              {new Date(document.uploaded_at).toLocaleDateString()}
            </span>
            {document.ocr_quality != null && (
              <span className="text-xs text-slate-400">OCR: {(document.ocr_quality * 100).toFixed(0)}%</span>
            )}
          </div>
        </div>

        {confirming ? (
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs text-slate-600 hidden sm:inline">Delete this document and everything derived from it?</span>
            <button
              onClick={() => setConfirming(false)}
              disabled={isDeleting}
              className="text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={() => onDelete(document.id)}
              disabled={isDeleting}
              className="text-xs font-medium px-3 py-1.5 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
            >
              {isDeleting ? 'Deleting…' : 'Confirm delete'}
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirming(true)}
            className="text-xs font-medium px-3 py-1.5 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 shrink-0"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => dataApi.documents().then((r) => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => {
      setDeletingId(id);
      return dataApi.deleteDocument(id);
    },
    onSuccess: () => {
      setError(null);
      // A document's cascade touches alerts, timeline events, and summary
      // counts too, so all of those need to refetch alongside the list.
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['timeline'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
    },
    onError: (err) => {
      const detail = isAxiosError(err) ? (err.response?.data as { detail?: string } | undefined)?.detail : undefined;
      setError(detail || 'Failed to delete document');
    },
    onSettled: () => setDeletingId(null),
  });

  if (isLoading) return <p className="text-slate-500">Loading documents...</p>;

  if (!documents?.length) {
    return (
      <div className="text-center py-16">
        <h1 className="text-2xl font-bold mb-2">Documents</h1>
        <p className="text-slate-500 mb-6 max-w-md mx-auto">
          No documents uploaded yet. Upload a prescription, lab report, or discharge summary to get started.
        </p>
        <Link to="/upload" className="text-blue-600 font-medium hover:underline">
          Go to Upload →
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6 flex-wrap gap-2">
        <h1 className="text-2xl font-bold">Documents</h1>
        <Link to="/upload" className="text-sm font-medium text-blue-600 hover:underline">
          + Upload more
        </Link>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
      )}

      <p className="text-sm text-slate-500 mb-3">
        Deleting a document also removes the visit, medications, lab results, and alerts derived from it.
      </p>

      <div className="bg-white rounded-xl border divide-y">
        {documents.map((d) => (
          <DocumentRow
            key={d.id}
            document={d}
            onDelete={(id) => deleteMutation.mutate(id)}
            isDeleting={deletingId === d.id}
          />
        ))}
      </div>
    </div>
  );
}
