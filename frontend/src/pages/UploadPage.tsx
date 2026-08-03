import { useCallback, useState } from 'react';
import { dataApi } from '../api/client';

interface UploadStatus {
  name: string;
  status: 'pending' | 'uploading' | 'done' | 'error';
  message?: string;
}

export default function UploadPage() {
  const [files, setFiles] = useState<UploadStatus[]>([]);
  const [dragging, setDragging] = useState(false);

  const uploadFiles = useCallback(async (fileList: FileList | File[]) => {
    const arr = Array.from(fileList);
    setFiles(arr.map((f) => ({ name: f.name, status: 'pending' })));

    for (let i = 0; i < arr.length; i++) {
      setFiles((prev) =>
        prev.map((f, idx) => (idx === i ? { ...f, status: 'uploading' } : f)),
      );
      try {
        const { data } = await dataApi.upload(arr[i]);
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: 'done', message: data.message } : f,
          ),
        );
      } catch {
        setFiles((prev) =>
          prev.map((f, idx) => (idx === i ? { ...f, status: 'error', message: 'Upload failed' } : f)),
        );
      }
    }
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Upload Documents</h1>
      <p className="text-slate-500 mb-6">Upload lab reports, prescriptions, discharge summaries, and doctor notes.</p>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragging ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-white'
        }`}
      >
        <p className="text-slate-600 mb-4">Drag & drop PDF, image, or text files here</p>
        <label className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-700">
          Browse Files
          <input
            type="file"
            accept=".pdf,.txt,.png,.jpg,.jpeg"
            multiple
            className="hidden"
            onChange={(e) => e.target.files && uploadFiles(e.target.files)}
          />
        </label>
      </div>

      {files.length > 0 && (
        <div className="mt-6 space-y-2">
          {files.map((f) => (
            <div key={f.name} className="bg-white border rounded-lg p-3 flex justify-between items-center">
              <span className="text-sm">{f.name}</span>
              <span className={`text-xs font-medium ${
                f.status === 'done' ? 'text-green-600' :
                f.status === 'error' ? 'text-red-600' :
                f.status === 'uploading' ? 'text-blue-600' : 'text-slate-400'
              }`}>
                {f.status === 'uploading' ? 'Processing...' : f.message || f.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
