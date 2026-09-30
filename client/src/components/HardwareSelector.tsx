import React from 'react';
import { Cpu } from 'lucide-react';

interface HardwareSelectorProps {
  selected: string;
  onSelect: (hardware: string) => void;
  targets: Record<string, any>;
}

export const HardwareSelector: React.FC<HardwareSelectorProps> = ({ selected, onSelect, targets }) => {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <Cpu size={24} /> Select Target Hardware
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {Object.entries(targets).map(([key, specs]: [string, any]) => (
          <button
            key={key}
            onClick={() => onSelect(key)}
            className={`p-4 rounded-lg border-2 transition text-left ${
              selected === key
                ? 'border-blue-600 bg-blue-50 shadow-md'
                : 'border-gray-200 hover:border-blue-300'
            }`}
          >
            <p className="font-semibold text-sm">{specs.name}</p>
            <p className="text-xs text-gray-600 mt-2">RAM: {specs.ramKb}KB</p>
            <p className="text-xs text-gray-600">Flash: {specs.flashKb}KB</p>
            <p className="text-xs text-gray-600">{specs.cpuMhz}MHz</p>
          </button>
        ))}
      </div>
    </div>
  );
};
