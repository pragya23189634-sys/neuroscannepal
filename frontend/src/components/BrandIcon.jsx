/** Subtle brain + neural network mark for NeuroScan Nepal */
export default function BrandIcon({ className = 'h-9 w-9' }) {
  return (
    <svg className={className} viewBox="0 0 40 40" fill="none" aria-hidden>
      <rect width="40" height="40" rx="8" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
      <path
        d="M20 9c-4.5 0-7.5 3.2-7.5 7.2 0 2.1.9 3.8 2.2 5.1-.8 1.1-1.2 2.4-1 3.8.3 2.2 2.1 3.9 4.3 3.9.6 0 1.2-.1 1.7-.4.5.8 1.4 1.3 2.3 1.3 2.2 0 4-1.7 4.3-3.9.2-1.4-.2-2.7-1-3.8 1.3-1.3 2.2-3 2.2-5.1C27.5 12.2 24.5 9 20 9z"
        stroke="rgba(103,232,249,0.7)"
        strokeWidth="1.2"
        fill="none"
      />
      <circle cx="14" cy="16" r="1.2" fill="rgba(34,211,238,0.8)" />
      <circle cx="20" cy="14" r="1.2" fill="rgba(34,211,238,0.6)" />
      <circle cx="26" cy="16" r="1.2" fill="rgba(34,211,238,0.8)" />
      <circle cx="20" cy="22" r="1.2" fill="rgba(56,189,248,0.7)" />
      <path d="M14 16 L20 14 L26 16 L20 22 Z" stroke="rgba(34,211,238,0.35)" strokeWidth="0.6" />
    </svg>
  )
}
