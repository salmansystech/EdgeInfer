export interface ModelInfo {
  name: string;
  type: string;
  framework: string;
  totalParams: number;
  layers: number;
  sizeMb: number;
  inputShape: number[];
  outputShape: number[];
}

export interface HardwareTarget {
  key: string;
  name: string;
  ramKb: number;
  flashKb: number;
  cpuMhz: number;
  powerMw: number;
}

export interface AnalysisResult {
  analysis: string;
  metrics: ModelInfo;
  targetHardware: string;
}

export interface OptimizationPlan {
  plan: string;
  level: 'conservative' | 'balanced' | 'aggressive';
  estimatedSizeReduction: number;
  estimatedLatencyImprovement: number;
}

export interface BenchmarkResult {
  originalSizeMb: number;
  optimizedSizeMb: number;
  sizeReductionPercent: number;
  estimatedLatencyMs: number;
  estimatedPowerMw: number;
  accuracyPreservation: number;
  deploymentReady: boolean;
}

export interface CodeResult {
  code: string;
  language: string;
  hardware: string;
}
