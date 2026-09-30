import React from 'react';
import { Zap } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <div className="container-main flex items-center justify-between py-6">
        <div className="flex items-center gap-3">
          <Zap size={32} className="text-yellow-300" />
          <div>
            <h1 className="text-3xl font-bold">EdgeInfer</h1>
            <p className="text-blue-100">Deploy AI to Edge Devices</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-blue-100">ML Model Optimization</p>
          <p className="font-semibold">Intelligent Deployment</p>
        </div>
      </div>
    </header>
  );
};
