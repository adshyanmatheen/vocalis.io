'use client'

import DotField from '@/components/DotField'
import { DotmSquare18 } from '@/components/ui/dotm-square-18'

const DOT_FIELD_PROPS = {
  dotRadius: 1.0,
  dotSpacing: 22,
  cursorRadius: 200,
  cursorForce: 0,
  bulgeOnly: false,
  bulgeStrength: 0,
  glowRadius: 210,
  sparkle: true,
  waveAmplitude: 0,
  gradientFrom: '#cbcbcb' as const,
  gradientTo: '#cbcbcb' as const,
}

export function PageBackground() {
  return (
    <div className="absolute inset-0 -z-10">
      <DotField {...DOT_FIELD_PROPS} />
    </div>
  )
}

interface DotMetersRowProps {
  mobileSize?: number
  desktopSize?: number
}

export function DotMetersRow({ mobileSize = 31, desktopSize = 48 }: DotMetersRowProps) {
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
            animated
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
            animated
            opacityBase={0.08}
            opacityMid={0.3}
            opacityPeak={1}
          />
        ))}
      </div>
    </>
  )
}
