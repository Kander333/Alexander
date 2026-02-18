import { useEffect, useMemo, useRef, useState } from 'react'

const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&'

export function GlitchText({ children, className = '', duration = 700 }) {
  const sourceText = useMemo(() => String(children), [children])
  const [displayText, setDisplayText] = useState(sourceText)
  const frameRef = useRef(null)

  useEffect(() => {
    setDisplayText(sourceText)
    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current)
      }
    }
  }, [sourceText])

  const runDecode = () => {
    if (frameRef.current) {
      cancelAnimationFrame(frameRef.current)
    }

    const start = performance.now()

    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1)
      const revealed = Math.floor(progress * sourceText.length)

      const scrambled = sourceText
        .split('')
        .map((char, index) => {
          if (char === ' ') return ' '
          if (index < revealed) return sourceText[index]
          return GLYPHS[Math.floor(Math.random() * GLYPHS.length)]
        })
        .join('')

      setDisplayText(scrambled)

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(step)
      }
    }

    frameRef.current = requestAnimationFrame(step)
  }

  return (
    <span className={className} onMouseEnter={runDecode} onFocus={runDecode}>
      {displayText}
    </span>
  )
}
