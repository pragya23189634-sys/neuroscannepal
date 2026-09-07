const CORNERS = [
  'top-1.5 left-1.5 border-t border-l',
  'top-1.5 right-1.5 border-t border-r',
  'bottom-1.5 left-1.5 border-b border-l',
  'bottom-1.5 right-1.5 border-b border-r',
]

const LABELS = [
  { text: 'AI ANALYSIS', className: 'left-2 top-2' },
  { text: 'MODEL ATTENTION', className: 'left-2 bottom-2 max-w-[72px] leading-tight' },
  { text: 'GRAD-CAM', className: 'right-2 top-2' },
]

function NeuralOverlay() {
  return (
    <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.22]" aria-hidden>
      <line x1="12%" y1="18%" x2="38%" y2="42%" stroke="rgba(82,199,217,0.5)" strokeWidth="0.5" />
      <line x1="38%" y1="42%" x2="62%" y2="28%" stroke="rgba(82,199,217,0.35)" strokeWidth="0.5" />
      <line x1="62%" y1="28%" x2="78%" y2="55%" stroke="rgba(82,199,217,0.4)" strokeWidth="0.5" />
      <circle cx="38%" cy="42%" r="2" fill="rgba(82,199,217,0.55)" />
      <circle cx="62%" cy="28%" r="2" fill="rgba(82,199,217,0.45)" />
    </svg>
  )
}

export default function MriHeroVisual({ className = '' }) {
  return (
    <div
      className={`relative aspect-square w-full overflow-hidden rounded-md bg-[#0c1524] ${className}`}
      style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.35), inset 0 0 0 1px rgba(77,141,219,0.12)' }}
    >
      <img
        src="/images/login-mri-hero.png"
        alt=""
        className="h-full w-full object-cover object-center opacity-[0.92]"
        draggable={false}
        onError={(e) => {
          e.currentTarget.style.display = 'none'
        }}
      />
      <MriFallbackSvg />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[#14233B]/20 via-transparent to-[#14233B]/60" />
      <NeuralOverlay />
      {CORNERS.map((pos) => (
        <span
          key={pos}
          className={`pointer-events-none absolute h-4 w-4 border-[#52C7D9]/40 ${pos}`}
          aria-hidden
        />
      ))}
      {LABELS.map(({ text, className: labelClass }) => (
        <span
          key={text}
          className={`pointer-events-none absolute rounded border border-white/[0.08] bg-[#14233B]/75 px-1.5 py-0.5 font-mono text-[6px] tracking-[0.12em] text-[#52C7D9]/70 ${labelClass}`}
        >
          {text}
        </span>
      ))}
    </div>
  )
}

function MriFallbackSvg() {
  return (
    <svg viewBox="0 0 200 200" className="absolute inset-0 h-full w-full" aria-hidden>
      <defs>
        <radialGradient id="mri-bg" cx="50%" cy="48%" r="50%">
          <stop offset="0%" stopColor="#3a424c" />
          <stop offset="55%" stopColor="#252b33" />
          <stop offset="100%" stopColor="#141a22" />
        </radialGradient>
        <radialGradient id="mri-heat" cx="38%" cy="52%" r="28%">
          <stop offset="0%" stopColor="rgba(239,68,68,0.55)" />
          <stop offset="35%" stopColor="rgba(234,179,8,0.4)" />
          <stop offset="60%" stopColor="rgba(80,201,165,0.28)" />
          <stop offset="85%" stopColor="rgba(77,141,219,0.15)" />
          <stop offset="100%" stopColor="rgba(77,141,219,0)" />
        </radialGradient>
        <clipPath id="mri-skull">
          <ellipse cx="100" cy="98" rx="72" ry="76" />
        </clipPath>
      </defs>
      <rect width="200" height="200" fill="#0c1524" />
      <g clipPath="url(#mri-skull)">
        <ellipse cx="100" cy="98" rx="70" ry="74" fill="url(#mri-bg)" />
        <ellipse cx="100" cy="98" rx="70" ry="74" fill="url(#mri-heat)" />
        <ellipse cx="100" cy="100" rx="9" ry="14" fill="#111820" opacity="0.7" />
      </g>
    </svg>
  )
}
