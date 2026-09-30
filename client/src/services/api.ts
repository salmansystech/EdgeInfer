import axios from 'axios';
import { ModelInfo, AnalysisResult, OptimizationPlan, BenchmarkResult, CodeResult } from '../types';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeModel = async (modelInfo: ModelInfo, hardware: string): Promise<AnalysisResult> => {
  const response = await api.post('/analyze', { modelInfo, hardware });
  return response.data;
};

export const generateOptimization = async (
  modelInfo: ModelInfo,
  hardware: string,
  level: 'conservative' | 'balanced' | 'aggressive'
): Promise<OptimizationPlan> => {
  const response = await api.post('/optimize', { modelInfo, hardware, level });
  return response.data;
};

export const generateCode = async (
  modelInfo: ModelInfo,
  hardware: string,
  optimizationPlan: OptimizationPlan
): Promise<CodeResult> => {
  const response = await api.post('/generate-code', { modelInfo, hardware, optimizationPlan });
  return response.data;
};

export const benchmarkModel = async (
  modelInfo: ModelInfo,
  hardware: string,
  techniques: string[]
): Promise<BenchmarkResult> => {
  const response = await api.post('/benchmark', { modelInfo, hardware, techniques });
  return response.data;
};

export const getHardwareTargets = async () => {
  const response = await api.get('/hardware-targets');
  return response.data;
};

export default api;
