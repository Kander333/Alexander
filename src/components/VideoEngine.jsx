import { useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { LOCATIONS } from '../config/nodes'
import { InterfaceLayer } from './InterfaceLayer'

const ENGINE_STATE = {
  IDLE: 'IDLE',
  TRANSITION: 'TRANSITION',
  ARRIVAL: 'ARRIVAL',
}

export function VideoEngine({ startNodeId = 'hub' }) {
  const [currentNodeId, setCurrentNodeId] = useState(startNodeId)
  const [engineState, setEngineState] = useState(ENGINE_STATE.IDLE)
  const [activeExit, setActiveExit] = useState(null)
  const [soundEnabled, setSoundEnabled] = useState(false)
  const [showManifesto, setShowManifesto] = useState(false)

  const loopVideoRef = useRef(null)
  const transitionVideoRef = useRef(null)

  const currentLocation = LOCATIONS[currentNodeId]

  useEffect(() => {
    const preloaded = []

    currentLocation?.exits.forEach((exit) => {
      const element = document.createElement('video')
      element.src = exit.transitionVideo
      element.preload = 'auto'
      preloaded.push(element)
    })

    return () => {
      preloaded.length = 0
    }
  }, [currentLocation])

  const transitionSource = useMemo(() => activeExit?.transitionVideo ?? '', [activeExit])

  useEffect(() => {
    const loopVideo = loopVideoRef.current

    if (!loopVideo) return

    loopVideo.loop = true
    loopVideo.muted = !soundEnabled

    if (engineState === ENGINE_STATE.IDLE || engineState === ENGINE_STATE.ARRIVAL) {
      void loopVideo.play().catch(() => {})
    }
  }, [currentNodeId, engineState, soundEnabled])

  useEffect(() => {
    const transitionVideo = transitionVideoRef.current
    if (!transitionVideo || engineState !== ENGINE_STATE.TRANSITION || !activeExit) return

    transitionVideo.currentTime = 0
    transitionVideo.muted = !soundEnabled
    void transitionVideo.play().catch(() => {})
  }, [activeExit, engineState, soundEnabled])

  const handleNavigate = (exit) => {
    if (engineState !== ENGINE_STATE.IDLE) return
    setActiveExit(exit)
    setEngineState(ENGINE_STATE.TRANSITION)
    setShowManifesto(false)

    if (loopVideoRef.current) {
      loopVideoRef.current.pause()
    }
  }

  const handleTransitionEnded = () => {
    if (!activeExit) return

    setCurrentNodeId(activeExit.targetId)
    setEngineState(ENGINE_STATE.ARRIVAL)

    requestAnimationFrame(() => {
      setActiveExit(null)
      setEngineState(ENGINE_STATE.IDLE)
    })
  }

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-void font-body text-primary">
      <video
        ref={loopVideoRef}
        key={currentLocation.videoLoop}
        className="absolute inset-0 h-full w-full object-cover"
        src={currentLocation.videoLoop}
        autoPlay
        muted={!soundEnabled}
        loop
        playsInline
      />

      <AnimatePresence>
        {engineState === ENGINE_STATE.TRANSITION && activeExit && (
          <motion.video
            ref={transitionVideoRef}
            key={transitionSource}
            className="absolute inset-0 z-10 h-full w-full object-cover"
            src={transitionSource}
            autoPlay
            playsInline
            muted={!soundEnabled}
            onEnded={handleTransitionEnded}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, ease: 'linear' }}
          />
        )}
      </AnimatePresence>

      <InterfaceLayer
        location={currentLocation}
        state={engineState}
        onNavigate={handleNavigate}
        onToggleManifesto={() => setShowManifesto((prev) => !prev)}
      />

      <button
        type="button"
        onClick={() => setSoundEnabled((prev) => !prev)}
        className="absolute bottom-4 right-4 z-30 border border-border-dim bg-black/60 px-3 py-2 font-heading text-[11px] tracking-[0.2em]"
      >
        SOUND {soundEnabled ? 'ON' : 'OFF'}
      </button>

      <AnimatePresence>
        {showManifesto && currentNodeId === 'manifesto' && (
          <motion.section
            className="absolute inset-0 z-40 flex items-center justify-center bg-black/80 p-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <article className="max-w-2xl border border-border-dim bg-void/90 p-6">
              <h2 className="mb-4 font-heading text-lg tracking-[0.22em] text-accent-signal">THE CONSTRUCT MANIFESTO</h2>
              <p className="mb-3 text-sm leading-relaxed text-primary/85">
                You are not browsing content. You are traversing memory. Each chamber is a state, each path
                is intent, each click rewrites your position inside the machine.
              </p>
              <p className="text-sm leading-relaxed text-primary/85">
                Preserve the signal. Reject linearity. Navigate the impossible architecture until meaning
                emerges from motion.
              </p>
            </article>
          </motion.section>
        )}
      </AnimatePresence>
    </div>
  )
}
