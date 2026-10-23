import React, { useState, useEffect } from 'react';
import { Code, FileSearch, Sparkles } from 'lucide-react';
import { Header } from './components/Header';
import { ModelUpload } from './components/ModelUpload';
import { HardwareSelector } from './components/HardwareSelector';
import { OptimizationSelector } from './components/OptimizationSelector';
import { ResultsDisplay } from './components/ResultsDisplay';
import { AgentOutput } from './components/AgentOutput';
import {
  getHardwareTargets,
  benchmarkModel,
  analyzeModel,
  generateOptimization,
  generateCode,
  getErrorMessage,
} from './services/api';
import { ModelInfo, BenchmarkResult, OptimizationPlan } from './types';
import './styles/index.css';

type Level = 'conservative' | 'balanced' | 'aggressive';

export const App: React.FC = () => {
  const [hardwareTargets, setHardwareTargets] = useState<Record<string, any>>({});
  const [selectedHardware, setSelectedHardware] = useState('esp32');
  const [optimizationLevel, setOptimizationLevel] = useState<Level>('balanced');
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [results, setResults] = useState<BenchmarkResult | null>(null);
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [plan, setPlan] = useState<OptimizationPlan | null>(null);
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState({ benchmark: false, analysis: false, plan: false, code: false });
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => {
    // Load hardware targets on mount
    getHardwareTargets()
      .then(setHardwareTargets)
      .catch((error) => setErrors([`Could not reach the backend: ${getErrorMessage(error)}`]));
  }, []);

  const resetResults = () => {
    setResults(null);
    setAnalysis(null);
    setPlan(null);
    setCode(null);
    setErrors([]);
  };

  const setStepLoading = (step: keyof typeof loading, value: boolean) =>
    setLoading((prev) => ({ ...prev, [step]: value }));

  const addError = (step: string, error: unknown) =>
    setErrors((prev) => [...prev, `${step} failed: ${getErrorMessage(error)}`]);

  const handleModelUpload = (file: File) => {
    // Only the file name and size come from the upload; the architecture fields
    // are example values until model file parsing is implemented
    const newModelInfo: ModelInfo = {
      name: file.name.replace(/\.[^/.]+$/, ''),
      type: 'Neural Network',
      framework: 'TensorFlow',
      totalParams: 3500000,
      layers: 154,
      sizeMb: file.size / (1024 * 1024),
      inputShape: [224, 224, 3],
      outputShape: [1000],
    };
    setModelInfo(newModelInfo);
    resetResults();
  };

  const handleHardwareSelect = (hardware: string) => {
    setSelectedHardware(hardware);
    resetResults();
  };

  const handleLevelSelect = (level: Level) => {
    setOptimizationLevel(level);
    resetResults();
  };

  const handleAnalyze = async () => {
    if (!modelInfo) return;
    resetResults();
    setLoading({ benchmark: true, analysis: true, plan: true, code: false });

    const runBenchmark = benchmarkModel(modelInfo, selectedHardware, optimizationLevel)
      .then(setResults)
      .catch((error) => addError('Benchmark', error))
      .finally(() => setStepLoading('benchmark', false));

    const runAnalysis = analyzeModel(modelInfo, selectedHardware)
      .then((result) => setAnalysis(result.analysis))
      .catch((error) => addError('Analysis', error))
      .finally(() => setStepLoading('analysis', false));

    const runOptimization = generateOptimization(modelInfo, selectedHardware, optimizationLevel)
      .then(setPlan)
      .catch((error) => addError('Optimization plan', error))
      .finally(() => setStepLoading('plan', false));

    await Promise.all([runBenchmark, runAnalysis, runOptimization]);
  };

  const handleGenerateCode = async () => {
    if (!modelInfo || !plan) return;
    setCode(null);
    setStepLoading('code', true);
    try {
      const result = await generateCode(modelInfo, selectedHardware, plan);
      setCode(result.code);
    } catch (error) {
      addError('Code generation', error);
    } finally {
      setStepLoading('code', false);
    }
  };

  const busy = Object.values(loading).some(Boolean);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="container-main">
        <div className="space-y-6">
          {errors.length > 0 && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 space-y-1">
              {errors.map((error, i) => <p key={i}>{error}</p>)}
            </div>
          )}

          {/* Model Upload Section */}
          <ModelUpload onUpload={handleModelUpload} />

          {modelInfo && (
            <>
              {/* Hardware Selection */}
              <HardwareSelector
                selected={selectedHardware}
                onSelect={handleHardwareSelect}
                targets={hardwareTargets}
              />

              {/* Optimization Level */}
              <OptimizationSelector
                selected={optimizationLevel}
                onSelect={handleLevelSelect}
              />

              {/* Analysis Button */}
              <div className="card text-center">
                <button
                  onClick={handleAnalyze}
                  disabled={busy}
                  className={`btn-primary disabled:opacity-50 disabled:cursor-not-allowed text-lg py-3 px-8`}
                >
                  {loading.analysis || loading.plan ? 'Analyzing...' : 'Analyze & Optimize'}
                </button>
                <p className="text-sm text-gray-500 mt-3">
                  Parameter count and layer count are example values until model file parsing is added.
                </p>
              </div>

              {/* Results */}
              <ResultsDisplay results={results} loading={loading.benchmark} />

              <AgentOutput
                title="Model Analysis"
                icon={<FileSearch size={24} />}
                text={analysis}
                loading={loading.analysis}
                loadingLabel="Claude is analyzing the model..."
                downloadName={`${modelInfo.name}-analysis.md`}
              />

              <AgentOutput
                title="Optimization Plan"
                icon={<Sparkles size={24} />}
                text={plan?.plan ?? null}
                loading={loading.plan}
                loadingLabel="Claude is writing the optimization plan..."
                downloadName={`${modelInfo.name}-optimization-plan.md`}
              />

              {plan && !code && !loading.code && (
                <div className="card text-center">
                  <button onClick={handleGenerateCode} disabled={busy} className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed text-lg py-3 px-8">
                    Generate Inference Code
                  </button>
                </div>
              )}

              <AgentOutput
                title="Inference Code"
                icon={<Code size={24} />}
                text={code}
                loading={loading.code}
                loadingLabel="Claude is generating C++ inference code..."
                downloadName={`${modelInfo.name}-inference.md`}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
