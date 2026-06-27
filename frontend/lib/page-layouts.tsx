'use client'

import { createContext, useContext, useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import DotField from '@/components/DotField'
import { DotmSquare18 } from '@/components/ui/dotm-square-18'

interface SparkleContextValue {
  sparkle: boolean
  setSparkle: (v: boolean) => void
}

const SparkleContext = createContext<SparkleContextValue | null>(null)

export function SparkleProvider({ children }: { children: React.ReactNode }) {
  const [sparkle, setSparkle] = useState(true)
  return (
    <SparkleContext.Provider value={{ sparkle, setSparkle }}>{children}</SparkleContext.Provider>
  )
}

export function useSparkle(): SparkleContextValue {
  const ctx = useContext(SparkleContext)
  if (!ctx) {
    return { sparkle: true, setSparkle: () => {} }
  }
  return ctx
}

const DOT_FIELD_PROPS = {
  dotRadius: 1.0,
  dotSpacing: 22,
  cursorRadius: 200,
  cursorForce: 0,
  bulgeOnly: false,
  bulgeStrength: 0,
  glowRadius: 210,
  waveAmplitude: 0,
  gradientFrom: '#cbcbcb' as const,
  gradientTo: '#cbcbcb' as const,
}

export function PageBackground() {
  const { sparkle, setSparkle } = useSparkle()

  return (
    <>
      <div className="fixed inset-0 -z-10">
        <DotField {...DOT_FIELD_PROPS} sparkle={sparkle} />
      </div>
      <button
        onClick={() => setSparkle(!sparkle)}
        aria-label={sparkle ? 'Disable sparkle effect' : 'Enable sparkle effect'}
        className="fixed bottom-4 right-4 z-50 flex size-10 cursor-pointer items-center justify-center border border-white/20 bg-black/60 text-white/80 transition-colors hover:border-white/40 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50"
      >
        {sparkle ? <EyeOff size={16} /> : <Eye size={16} />}
      </button>
    </>
  )
}

interface DotMetersRowProps {
  mobileSize?: number
  desktopSize?: number
}

export function DotMetersRow({ mobileSize = 31, desktopSize = 48 }: DotMetersRowProps) {
  const { sparkle } = useSparkle()
  const dots = Array.from({ length: 8 })
  return (
    <>
      <div className="mt-8 flex items-center justify-center gap-1.5 sm:hidden">
        {dots.map((_, i) => (
          <DotmSquare18
            key={i}
            size={mobileSize}
            dotSize={2}
            speed={1 + i * 0.1}
            pattern="full"
            color="#ffffff"
            animated={sparkle}
            opacityBase={0.08}
            opacityMid={0.3}
            opacityPeak={1}
          />
        ))}
      </div>
      <div className="mt-10 hidden items-center justify-center gap-2 sm:flex">
        {dots.map((_, i) => (
          <DotmSquare18
            key={i}
            size={desktopSize}
            dotSize={2}
            speed={1 + i * 0.1}
            pattern="full"
            color="#ffffff"
            animated={sparkle}
            opacityBase={0.08}
            opacityMid={0.3}
            opacityPeak={1}
          />
        ))}
      </div>
    </>
  )
}
