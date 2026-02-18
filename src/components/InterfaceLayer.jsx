import { motion } from 'framer-motion'
import { GlitchText } from './GlitchText'

export function InterfaceLayer({ location, state, onNavigate, onToggleManifesto }) {
  if (!location) return null

  return (
    <div className="pointer-events-none absolute inset-0 z-20 text-primary font-heading">
      <div className="absolute left-4 top-4 border border-border-dim bg-black/30 px-3 py-2 text-xs tracking-[0.25em]">
        <GlitchText>{location.title}</GlitchText>
      </div>

      {location.id === 'manifesto' && (
        <button
          type="button"
          onClick={onToggleManifesto}
          className="pointer-events-auto absolute right-4 top-4 border border-accent-signal/70 bg-black/50 px-3 py-2 text-xs tracking-[0.2em] text-accent-signal"
        >
          OPEN PROTOCOL
        </button>
      )}

      {location.exits.map((exit) => (
        <motion.button
          key={`${location.id}-${exit.targetId}`}
          type="button"
          onClick={() => onNavigate(exit)}
          disabled={state !== 'IDLE'}
          className="pointer-events-auto absolute -translate-x-1/2 -translate-y-1/2 border border-border-dim bg-black/45 px-3 py-2 text-[11px] tracking-[0.18em] transition-colors disabled:cursor-not-allowed disabled:opacity-40"
          style={{ left: `${exit.coordinates.x}%`, top: `${exit.coordinates.y}%` }}
          whileHover={{ scale: 1.06, boxShadow: '0 0 12px rgba(255, 77, 0, 0.6)' }}
          whileTap={{ scale: 0.97 }}
        >
          <GlitchText>{exit.label}</GlitchText>
        </motion.button>
      ))}
    </div>
  )
}
