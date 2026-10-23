import React from 'react';
import { Download } from 'lucide-react';

interface AgentOutputProps {
  title: string;
  icon: React.ReactNode;
  text: string | null;
  loading: boolean;
  loadingLabel: string;
  downloadName?: string;
}

export const AgentOutput: React.FC<AgentOutputProps> = ({ title, icon, text, loading, loadingLabel, downloadName }) => {
  if (!loading && !text) {
    return null;
  }

  const handleDownload = () => {
    if (!text || !downloadName) return;
    const url = URL.createObjectURL(new Blob([text], { type: 'text/markdown' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = downloadName;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4 gap-4">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          {icon} {title}
        </h2>
        {text && downloadName && (
          <button onClick={handleDownload} className="btn-secondary flex items-center gap-2">
            <Download size={16} /> Download
          </button>
        )}
      </div>
      {loading ? (
        <div className="flex items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-gray-600">{loadingLabel}</span>
        </div>
      ) : (
        <pre className="whitespace-pre-wrap break-words text-sm bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-[32rem] overflow-y-auto font-mono">
          {text}
        </pre>
      )}
    </div>
  );
};
