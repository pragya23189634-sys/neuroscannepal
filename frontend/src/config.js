export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export const PIPELINE_STEPS = [
  { key: 'upload', label: 'Upload' },
  { key: 'preprocessing', label: 'Preprocessing (CLAHE + QC)' },
  { key: 'detection', label: 'CNN Detection' },
  { key: 'gradcam', label: 'Grad-CAM Explainability' },
  { key: 'rag_advisory', label: 'RAG Medical Advisory' },
  { key: 'chatbot', label: 'Bilingual Chatbot' },
  { key: 'hospital_finder', label: 'Hospital Finder' },
  { key: 'pdf_report', label: 'Report Generation' },
]

export const MODEL_INFO = {
  name: 'Baseline CNN',
  version: 'v1.1',
  validationAccuracy: '97.81%',
  balancedAccuracy: '98.12%',
  trainSamples: 1280,
  valSamples: 320,
  inputSize: '128 × 128 grayscale',
  classes: ['Normal', 'Abnormal'],
}
