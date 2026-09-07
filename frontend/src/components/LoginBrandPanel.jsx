import React from 'react'
import {
  BeakerIcon,
  ChevronRightIcon,
  CloudArrowUpIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  EyeIcon,
  SparklesIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import BrandIcon from './BrandIcon'
import MriHeroVisual from './MriHeroVisual'
import { BRAND, LOGIN_PANEL } from '../content/siteCopy'

const FEATURE_ICONS = [BeakerIcon, EyeIcon, UserGroupIcon]
const WORKFLOW_ICONS = [CloudArrowUpIcon, Cog6ToothIcon, EyeIcon, DocumentTextIcon]

const BADGE_ICONS = {
  cyan: SparklesIcon,
  blue: EyeIcon,
  green: UserGroupIcon,
}

function HimalayaSilhouette() {
  return (
    <svg className="h-3.5 w-3.5 shrink-0 text-[#55C7D9]/35" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M1 19 L5 11 L9 14 L13 7 L17 12 L21 9 L23 19 Z"
        stroke="currentColor"
        strokeWidth="0.9"
        fill="rgba(85,199,217,0.08)"
      />
    </svg>
  )
}

export default function LoginBrandPanel() {
  return (
    <aside className="login-panel">
      <div className="hero-grid pointer-events-none absolute inset-0 opacity-[0.1]" aria-hidden />
      <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-12 opacity-[0.12]" aria-hidden>
        <svg className="h-full w-full" viewBox="0 0 1200 48" preserveAspectRatio="none">
          <path
            fill="rgba(85,199,217,0.22)"
            d="M0 48 L0 36 L80 28 L160 34 L240 24 L320 32 L400 22 L480 30 L560 20 L640 28 L720 24 L800 32 L880 26 L960 34 L1040 28 L1120 36 L1200 30 L1200 48 Z"
          />
        </svg>
      </div>

      <div className="login-panel-inner">
        {/* Top: brand (left) + MRI (right) — grid, no overlap */}
        <div className="login-header-grid">
          <div className="login-brand-col">
            <div className="flex items-start gap-2.5">
              <BrandIcon className="mt-0.5 h-8 w-8 shrink-0" />
              <div>
                <h1 className="login-brand-title">
                  <span className="text-white">{BRAND.namePart1}</span>{' '}
                  <span className="text-[#55C7D9]">{BRAND.namePart2}</span>
                </h1>
                <p className="login-tagline">{LOGIN_PANEL.tagline}</p>
              </div>
            </div>
            <p className="login-mission">{LOGIN_PANEL.mission}</p>
          </div>
          <div className="login-mri-col">
            <MriHeroVisual />
          </div>
        </div>

        {/* Feature cards — full width, below header */}
        <div className="login-feature-grid">
          {LOGIN_PANEL.features.map((feature, i) => {
            const Icon = FEATURE_ICONS[i]
            return (
              <div key={feature.number} className="login-feature-card">
                <div className="flex items-start justify-between gap-2">
                  <span className="login-feature-number">{feature.number}</span>
                  <Icon className="h-3.5 w-3.5 shrink-0 text-[#55C7D9]/60" strokeWidth={1.5} />
                </div>
                <p className="login-feature-title">{feature.title}</p>
                <p className="login-feature-desc">{feature.description}</p>
              </div>
            )
          })}
        </div>

        {/* Workflow */}
        <div className="login-workflow">
          <p className="login-workflow-heading">{LOGIN_PANEL.workflowTitle}</p>
          <div className="login-workflow-steps">
            {LOGIN_PANEL.workflow.map((item, i) => {
              const Icon = WORKFLOW_ICONS[i]
              return (
                <React.Fragment key={item.step}>
                  <div className="login-workflow-step">
                    <div className="login-workflow-icon">
                      <Icon className="h-3.5 w-3.5 text-[#55C7D9]/65" strokeWidth={1.5} />
                    </div>
                    <p className="login-workflow-label">{item.step}</p>
                    <p className="login-workflow-hint">{item.hint}</p>
                  </div>
                  {i < LOGIN_PANEL.workflow.length - 1 && (
                    <ChevronRightIcon className="login-workflow-arrow" strokeWidth={2} />
                  )}
                </React.Fragment>
              )
            })}
          </div>
        </div>

        {/* Nepal + badges + footer */}
        <div className="login-bottom">
          <div className="login-nepal">
            <HimalayaSilhouette />
            <div>
              <p className="login-nepal-title">{LOGIN_PANEL.nepalTitle}</p>
              <p className="login-nepal-support">{LOGIN_PANEL.nepalSupport}</p>
            </div>
          </div>
          <div className="login-bottom-row">
            <p className="login-footer-text">{BRAND.institution}</p>
            <div className="login-badges">
              {LOGIN_PANEL.badges.map((badge) => {
                const Icon = BADGE_ICONS[badge.accent]
                const accentClass =
                  badge.accent === 'cyan'
                    ? 'border-[#55C7D9]/25 text-[#55C7D9]/80 bg-[#55C7D9]/[0.04]'
                    : badge.accent === 'blue'
                      ? 'border-[#4D8DDB]/25 text-[#4D8DDB]/80 bg-[#4D8DDB]/[0.04]'
                      : 'border-[#50C9A5]/25 text-[#50C9A5]/80 bg-[#50C9A5]/[0.04]'
                return (
                  <span key={badge.label} className={`login-badge ${accentClass}`}>
                    <Icon className="h-2 w-2 opacity-70" strokeWidth={2} />
                    {badge.label}
                  </span>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
