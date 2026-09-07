import React from 'react'
import PageHeader from '../components/PageHeader'
import { ABOUT, PAGES } from '../content/siteCopy'

export default function About() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={PAGES.about.eyebrow}
        title={PAGES.about.title}
        description={PAGES.about.description}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">What it does</h3>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">{ABOUT.aim}</p>
        </section>

        <section className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Project details</h3>
          <dl className="mt-4 space-y-2 text-sm">
            <div><dt className="text-slate-500">Student</dt><dd className="font-medium text-slate-900">Pragya Gajurel (23189634)</dd></div>
            <div><dt className="text-slate-500">Supervisor</dt><dd className="font-medium text-slate-900">Satyam Paudel</dd></div>
            <div><dt className="text-slate-500">Programme</dt><dd className="font-medium text-slate-900">BSc (Hons) Computer and Data Science</dd></div>
            <div><dt className="text-slate-500">Institution</dt><dd className="font-medium text-slate-900">Birmingham City University</dd></div>
            <div><dt className="text-slate-500">Contact</dt><dd className="font-medium text-accent">gajurelpragya@gmail.com</dd></div>
          </dl>
        </section>
      </div>

      <section className="card border-amber-200 bg-amber-50/60 p-6">
        <h3 className="text-lg font-semibold text-amber-900">Disclaimer</h3>
        <p className="mt-2 text-sm leading-relaxed text-amber-900/90">{ABOUT.disclaimer}</p>
      </section>
    </div>
  )
}
