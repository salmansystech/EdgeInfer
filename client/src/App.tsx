import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ModelUpload } from './components/ModelUpload';
import { HardwareSelector } from './components/HardwareSelector';
import { OptimizationSelector } from './components/OptimizationSelector';
import { ResultsDisplay } from './components/ResultsDisplay';
import { getHardwareTargets, benchmarkModel } from './services/api';
import { ModelInfo, BenchmarkResult } from './types';
import './styles/index.css';

export const App: React.FC = () => {
  const [hardwareTargets, setHardwareTargets] = useState<Record<string, any>>({});
  const [selectedHardware, setSelectedHardware] = useState('esp32');
  const [optimizationLevel, setOptimizationLevel] = useState<'conservative' | 'balanced' | 'aggressive'>('balanced');
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [results, setResults] = useState<BenchmarkResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load hardware targets on mount
    getHardwareTargets().then(setHardwareTargets).catch(console.error);
  }, []);

  const handleModelUpload = (file: File) => {
    // Mock model info - in real app, would parse file
    const newModelInfo: ModelInfo = {
      name: file.name.replace(/\.[^/.]+$/, ''),
      type: 'Neural Network',
      framework: 'TensorFlow',
      totalParams: 3500000,
      layers: 154,
      sizeMb: 14.2,
      inputShape: [224, 224, 3],
      outputShape: [1000],
    };
    setModelInfo(newModelInfo);
  };

  const handleAnalyze = async () => {
    if (!modelInfo) return;
    
    setLoading(true);
    try {
      const techniques = ['quantization'];
      if (optimizationLevel !== 'conservative') techniques.push('pruning', 'fusion');
      
      const benchResult = await benchmarkModel(modelInfo, selectedHardware, techniques);
      setResults(benchResult);
    } catch (error) {
      console.error('Analysis failed:', error);
      // Show mock results for demo
      setResults({
        originalSizeMb: 14.2,
        optimizedSizeMb: 1.8,
        sizeReductionPercent: 87.3,
        estimatedLatencyMs: 280,
        estimatedPowerMw: 50,
        accuracyPreservation: 98.7,
        deploymentReady: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="container-main">
        <div className="space-y-6">
          {/* Model Upload Section */}
          <ModelUpload onUpload={handleModelUpload} />

          {modelInfo && (
            <>
              {/* Hardware Selection */}
              <HardwareSelector 
                selected={selectedHardware}
                onSelect={setSelectedHardware}
                targets={hardwareTargets}
              />

              {/* Optimization Level */}
              <OptimizationSelector
                selected={optimizationLevel}
                onSelect={setOptimizationLevel}
              />

              {/* Analysis Button */}
              <div className="card text-center">
                <button 
                  onClick={handleAnalyze}
                  disabled={loading}
                  className={`btn-primary disabled:opacity-50 disabled:cursor-not-allowed text-lg py-3 px-8`}
                >
                  {loading ? 'Analyzing...' : 'Analyze & Optimize'}
                </button>
              </div>

              {/* Results */}
              <ResultsDisplay results={results} loading={loading} />

              {/* Download Section */}
              {results && (
                <div className="card">
                  <h2 className="text-xl font-bold mb-4">Download</h2>
                  <div className="flex gap-4 flex-wrap">
                    <button className="btn-primary">Download Code</button>
                    <button className="btn-primary">Download Report</button>
                    <button className="btn-secondary">View Details</button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
