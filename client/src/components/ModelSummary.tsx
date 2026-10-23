import React from 'react';
import { Box } from 'lucide-react';
import { ModelInfo } from '../types';

interface ModelSummaryProps {
  model: ModelInfo;
}

const formatShape = (shape: number[]) =>
  shape.length ? `[${shape.map((d) => (d < 0 ? '?' : d)).join(', ')}]` : 'Unknown';

const formatSize = (sizeMb: number) =>
  sizeMb >= 1 ? `${sizeMb.toFixed(2)} MB` : `${(sizeMb * 1024).toFixed(1)} KB`;

export const ModelSummary: React.FC<ModelSummaryProps> = ({ model }) => {
  const stats = [
    { label: 'Parameters', value: model.totalParams.toLocaleString() },
    { label: 'MACs', value: model.macs.toLocaleString() },
    { label: 'Layers', value: model.layers.toString() },
    { label: 'Precision', value: model.precision },
    { label: 'File Size', value: formatSize(model.sizeMb) },
    { label: 'Input', value: formatShape(model.inputShape) },
    { label: 'Output', value: formatShape(model.outputShape) },
  ];

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-1 flex items-center gap-2">
        <Box size={24} /> {model.name}
      </h2>
      <p className="text-gray-600 mb-4">{model.framework} model</p>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 mb-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">{stat.label}</p>
            <p className="font-semibold break-words">{stat.value}</p>
          </div>
        ))}
      </div>

      <p className="text-sm text-gray-500 mb-2">Operators</p>
      <div className="flex flex-wrap gap-2">
        {Object.entries(model.operators).map(([name, count]) => (
          <span key={name} className="bg-blue-50 text-blue-800 text-xs font-mono px-2 py-1 rounded">
            {name} ×{count}
          </span>
        ))}
      </div>
    </div>
  );
};
