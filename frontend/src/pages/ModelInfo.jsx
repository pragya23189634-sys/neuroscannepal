import React from 'react'
import { MODEL_INFO } from '../config'
import PageHeader from '../components/PageHeader'

export default function ModelInfo() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Machine learning"
        title="Model information"
        description="Details of the baseline convolutional neural network used for brain MRI abnormality screening in this prototype."
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Architecture</h3>
          <dl className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Model</dt><dd className="font-medium text-slate-900">{MODEL_INFO.name}</dd></div>
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Version</dt><dd className="font-medium text-slate-900">{MODEL_INFO.version}</dd></div>
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Input</dt><dd className="font-medium text-slate-900">{MODEL_INFO.inputSize}</dd></div>
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Classes</dt><dd className="font-medium text-slate-900">{MODEL_INFO.classes.join(' / ')}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Layers</dt><dd className="font-medium text-slate-900">3 conv blocks + dense classifier</dd></div>
          </dl>
        </section>

        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Training & evaluation</h3>
          <dl className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Validation accuracy</dt><dd className="font-semibold text-emerald-700">{MODEL_INFO.validationAccuracy}</dd></div>
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Training samples</dt><dd className="font-medium text-slate-900">{MODEL_INFO.trainSamples}</dd></div>
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Validation samples</dt><dd className="font-medium text-slate-900">{MODEL_INFO.valSamples}</dd></div>
            <div className="flex justify-between border-b border-slate-100 pb-2"><dt className="text-slate-500">Dataset size</dt><dd className="font-medium text-slate-900">1,600 MRI images</dd></div>
            <div className="flex justify-between"><dt className="text-slate-500">Preprocessing</dt><dd className="font-medium text-slate-900">CLAHE + resize + augment</dd></div>
          </dl>
        </section>
      </div>

      <section className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900">Explainability & integration</h3>
        <ul className="mt-4 grid gap-3 text-sm text-slate-700 md:grid-cols-2">
          <li className="rounded-xl bg-slate-50 px-4 py-3">Grad-CAM heatmaps highlight regions influencing the CNN decision</li>
          <li className="rounded-xl bg-slate-50 px-4 py-3">Low-contrast QC gate flags unreliable inputs before classification</li>
          <li className="rounded-xl bg-slate-50 px-4 py-3">RAG prototype provides contextual medical advisory text</li>
          <li className="rounded-xl bg-slate-50 px-4 py-3">Full pipeline logged step-by-step for integration testing</li>
        </ul>
      </section>
    </div>
  )
}
