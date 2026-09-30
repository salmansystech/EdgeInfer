import React from 'react';
import { CheckCircle, TrendingDown, Zap } from 'lucide-react';
import { BenchmarkResult } from '../types';

interface ResultsDisplayProps {
  results: BenchmarkResult | null;
  loading: boolean;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, loading }) => {
  if (loading) {
    return (
      <div className="card">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-4">Analyzing model...</span>
        </div>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <CheckCircle size={24} className="text-green-600" /> Optimization Results
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
          <p className="text-gray-600 font-semibold mb-2">Model Size</p>
          <div className="flex items-end gap-2">
            <div>
              <p className="text-3xl font-bold">{results.optimizedSizeMb.toFixed(1)}</p>
              <p className="text-sm text-gray-500">MB (optimized)</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">{results.originalSizeMb.toFixed(1)} MB (original)</p>
              <p className="text-lg font-bold text-green-600">{results.sizeReductionPercent.toFixed(1)}% ↓</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 rounded-lg">
          <p className="text-gray-600 font-semibold mb-2">Inference Latency</p>
          <div>
            <p className="text-3xl font-bold">{results.estimatedLatencyMs.toFixed(1)}</p>
            <p className="text-sm text-gray-500">milliseconds</p>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
          <p className="text-gray-600 font-semibold mb-2">Power Consumption</p>
          <div>
            <p className="text-3xl font-bold">{results.estimatedPowerMw.toFixed(1)}</p>
            <p className="text-sm text-gray-500">milliwatts (estimated)</p>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg">
          <p className="text-gray-600 font-semibold mb-2">Accuracy Preserved</p>
          <div>
            <p className="text-3xl font-bold">{results.accuracyPreservation.toFixed(1)}%</p>
            <p className="text-sm text-gray-500">of original</p>
          </div>
        </div>
      </div>

      <div className="border-t pt-6">
        <p className="text-lg font-semibold mb-4">Deployment Status</p>
        <div className={`p-4 rounded-lg ${results.deploymentReady ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}>
          <p className={`font-bold ${results.deploymentReady ? 'text-green-700' : 'text-yellow-700'}`}>
            {results.deploymentReady ? '✓ READY FOR DEPLOYMENT' : '⚠ NEEDS ADJUSTMENT'}
          </p>
        </div>
      </div>
    </div>
  );
};
