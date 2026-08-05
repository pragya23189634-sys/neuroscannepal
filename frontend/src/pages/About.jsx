import React from 'react'
import PageHeader from '../components/PageHeader'

export default function About() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Project"
        title="About NeuroScan Nepal"
        description="An AI-assisted brain MRI screening platform developed as a final-year research project, combining deep learning, explainability, and clinical workflow support for Nepal."
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Research aim</h3>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            NeuroScan Nepal demonstrates how automated MRI analysis can support early abnormality screening in
            resource-limited settings. The system integrates preprocessing, CNN classification, Grad-CAM
            explainability, and prototype clinical support modules (RAG advisory, bilingual chatbot, hospital finder).
          </p>
        </section>

        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Student & institution</h3>
          <dl className="mt-4 space-y-2 text-sm">
            <div><dt className="text-slate-500">Student</dt><dd className="font-medium text-slate-900">Pragya Gajurel (23189634)</dd></div>
            <div><dt className="text-slate-500">Programme</dt><dd className="font-medium text-slate-900">BSc (Hons) Computer and Data Science</dd></div>
            <div><dt className="text-slate-500">Institution</dt><dd className="font-medium text-slate-900">Birmingham City University · Sunway College Kathmandu</dd></div>
            <div><dt className="text-slate-500">Contact</dt><dd className="font-medium text-primary">gajurelpragya@gmail.com</dd></div>
          </dl>
        </section>
      </div>

      <section className="card border-amber-200 bg-amber-50/60 p-6">
        <h3 className="text-lg font-semibold text-amber-900">Ethics & disclaimer</h3>
        <p className="mt-2 text-sm leading-relaxed text-amber-900/90">
          This is a research prototype for academic evaluation and usability testing. It is not a certified medical
          device and must not be used for clinical diagnosis. All participant data in usability studies should follow
          the approved information sheet and consent procedures.
        </p>
      </section>
    </div>
  )
}
