import React from 'react';
import { Zap } from 'lucide-react';

interface OptimizationSelectorProps {
  selected: 'conservative' | 'balanced' | 'aggressive';
  onSelect: (level: 'conservative' | 'balanced' | 'aggressive') => void;
}

export const OptimizationSelector: React.FC<OptimizationSelectorProps> = ({ selected, onSelect }) => {
  const options = [
    { id: 'conservative', label: 'Conservative', desc: 'Maximum accuracy', selectedClass: 'border-green-600 bg-green-50' },
    { id: 'balanced', label: 'Balanced', desc: 'Good trade-off', selectedClass: 'border-blue-600 bg-blue-50' },
    { id: 'aggressive', label: 'Aggressive', desc: 'Maximum compression', selectedClass: 'border-red-600 bg-red-50' },
  ] as const;

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <Zap size={24} /> Optimization Level
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {options.map((opt) => (
          <button
            key={opt.id}
            onClick={() => onSelect(opt.id)}
            className={`p-4 rounded-lg border-2 transition ${
              selected === opt.id
                ? `${opt.selectedClass} shadow-md`
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <p className="font-semibold">{opt.label}</p>
            <p className="text-sm text-gray-600">{opt.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
};
