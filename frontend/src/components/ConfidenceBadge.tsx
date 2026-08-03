export default function ConfidenceBadge({ confidence }: { confidence: number }) {
  const color =
    confidence >= 70 ? 'bg-green-100 text-green-800' : confidence >= 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {confidence}% confidence
    </span>
  );
}
