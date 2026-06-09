'use client'

import { animate } from 'motion/react'
import type { HTMLAttributes } from 'react'
import { forwardRef, useCallback, useEffect, useImperativeHandle, useRef } from 'react'

import { cn } from '@/lib/utils'

export interface GripIconHandle {
  startAnimation: () => void
  stopAnimation: () => void
}

interface GripProps extends HTMLAttributes<HTMLDivElement> {
  size?: number
}

const CIRCLES = [
  { cx: 19, cy: 5 },
  { cx: 19, cy: 12 },
  { cx: 12, cy: 5 },
  { cx: 19, cy: 19 },
  { cx: 12, cy: 12 },
  { cx: 5, cy: 5 },
  { cx: 12, cy: 19 },
  { cx: 5, cy: 12 },
  { cx: 5, cy: 19 },
]

const ANIMATION_DURATION = 1.1
const STAGGER_DELAY = 0.07

const GripIcon = forwardRef<GripIconHandle, GripProps>(
  ({ onMouseEnter, onMouseLeave, className, size = 28, ...props }, ref) => {
    const svgRef = useRef<SVGSVGElement>(null)
    const isControlledRef = useRef(false)
    const isAnimatingRef = useRef(false)
    const isMountedRef = useRef(false)

    useEffect(() => {
      isMountedRef.current = true

      return () => {
        isMountedRef.current = false
      }
    }, [])

    const startAnimation = useCallback(() => {
      if (!isMountedRef.current) return
      if (isAnimatingRef.current) return
      isAnimatingRef.current = true

      const circles = svgRef.current?.querySelectorAll('circle')
      if (!circles || circles.length === 0) {
        isAnimatingRef.current = false
        return
      }

      circles.forEach((circle, index) => {
        animate(
          circle,
          { opacity: [1, 0.3, 0.3, 1] },
          {
            duration: ANIMATION_DURATION,
            delay: index * STAGGER_DELAY,
            times: [0, 0.2, 0.8, 1],
            onComplete: () => {
              if (!isMountedRef.current) return
              animate(circle, { opacity: 1 }, { duration: 0.25 })
              if (index === circles.length - 1) {
                isAnimatingRef.current = false
              }
            },
          },
        )
      })
    }, [])

    const stopAnimation = useCallback(() => {
      if (!isMountedRef.current) return
      if (!isAnimatingRef.current) return

      const circles = svgRef.current?.querySelectorAll('circle')
      if (!circles) return

      circles.forEach((circle) => {
        animate(circle, { opacity: 1 }, { duration: 0.25 })
      })
      isAnimatingRef.current = false
    }, [])

    useImperativeHandle(ref, () => {
      isControlledRef.current = true
      return { startAnimation, stopAnimation }
    })

    const handleMouseEnter = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (isControlledRef.current) {
          onMouseEnter?.(e)
        } else {
          startAnimation()
        }
      },
      [startAnimation, onMouseEnter],
    )

    const handleMouseLeave = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (isControlledRef.current) {
          onMouseLeave?.(e)
        } else {
          stopAnimation()
        }
      },
      [stopAnimation, onMouseLeave],
    )

    return (
      <div
        className={cn('inline-flex items-center justify-center', className)}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        {...props}
      >
        <svg
          fill="none"
          height={size}
          ref={svgRef}
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          width={size}
          xmlns="http://www.w3.org/2000/svg"
        >
          {CIRCLES.map((circle) => (
            <circle cx={circle.cx} cy={circle.cy} key={`${circle.cx}-${circle.cy}`} r="1" />
          ))}
        </svg>
      </div>
    )
  },
)

GripIcon.displayName = 'GripIcon'

export { GripIcon }
