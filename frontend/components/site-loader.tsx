import { DotmSquare1 } from '@/components/ui/dotm-square-1'

function BloomGlow() {
  return (
    <DotmSquare1
      size={63}
      dotSize={4}
      speed={1.1}
      pattern="full"
      colorPreset="solid-theme"
      animated
      opacityBase={0.12}
      opacityMid={0.42}
      opacityPeak={1}
    />
  )
}

export default function SiteLoader() {
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-background">
      <BloomGlow />
    </div>
  )
}
