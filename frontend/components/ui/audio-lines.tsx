'use client'

import { motion, useAnimation } from 'motion/react'
import type { HTMLAttributes } from 'react'
import { forwardRef, useCallback, useEffect, useImperativeHandle, useRef } from 'react'

import { cn } from '@/lib/utils'

export interface AudioLinesIconHandle {
  startAnimation: () => void
  stopAnimation: () => void
}

interface AudioLinesIconProps extends HTMLAttributes<HTMLDivElement> {
  size?: number
}

const AudioLinesIcon = forwardRef<AudioLinesIconHandle, AudioLinesIconProps>(
  ({ onMouseEnter, onMouseLeave, className, size = 28, style, ...props }, ref) => {
    const controls = useAnimation()
    const isControlledRef = useRef(false)
    const isMountedRef = useRef(false)

    useEffect(() => {
      isMountedRef.current = true

      return () => {
        isMountedRef.current = false
      }
    }, [])

    useImperativeHandle(ref, () => {
      isControlledRef.current = true

      return {
        startAnimation: () => {
          if (!isMountedRef.current) {
            return
          }

          void controls.start('animate')
        },
        stopAnimation: () => {
          if (!isMountedRef.current) {
            return
          }

          controls.stop()
          controls.set('normal')
        },
      }
    })

    const handleMouseEnter = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (isControlledRef.current) {
          onMouseEnter?.(e)
        } else {
          void controls.start('animate')
        }
      },
      [controls, onMouseEnter],
    )

    const handleMouseLeave = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (isControlledRef.current) {
          onMouseLeave?.(e)
        } else {
          controls.stop()
          controls.set('normal')
        }
      },
      [controls, onMouseLeave],
    )

    return (
      <div
        className={cn('inline-flex shrink-0 items-center justify-center', className)}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        style={{
          width: size,
          height: size,
          ...style,
        }}
        {...props}
      >
        <svg
          className="size-full"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M2 10v3" />
          <motion.path
            animate={controls}
            d="M6 6v11"
            initial="normal"
            style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
            variants={{
              normal: { opacity: 1, scaleY: 1 },
              animate: {
                opacity: [1, 0.72, 1],
                scaleY: [1, 0.68, 1],
                transition: {
                  duration: 1.5,
                  repeat: Number.POSITIVE_INFINITY,
                },
              },
            }}
          />
          <motion.path
            animate={controls}
            d="M10 3v18"
            initial="normal"
            style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
            variants={{
              normal: { opacity: 1, scaleY: 1 },
              animate: {
                opacity: [1, 0.68, 1],
                scaleY: [1, 0.58, 1],
                transition: {
                  duration: 1,
                  repeat: Number.POSITIVE_INFINITY,
                },
              },
            }}
          />
          <motion.path
            animate={controls}
            d="M14 8v7"
            initial="normal"
            style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
            variants={{
              normal: { opacity: 1, scaleY: 1 },
              animate: {
                opacity: [1, 0.74, 1],
                scaleY: [1, 1.35, 1],
                transition: {
                  duration: 0.8,
                  repeat: Number.POSITIVE_INFINITY,
                },
              },
            }}
          />
          <motion.path
            animate={controls}
            d="M18 5v13"
            initial="normal"
            style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
            variants={{
              normal: { opacity: 1, scaleY: 1 },
              animate: {
                opacity: [1, 0.7, 1],
                scaleY: [1, 0.64, 1],
                transition: {
                  duration: 1.5,
                  repeat: Number.POSITIVE_INFINITY,
                },
              },
            }}
          />
          <path d="M22 10v3" />
        </svg>
      </div>
    )
  },
)

AudioLinesIcon.displayName = 'AudioLinesIcon'

export { AudioLinesIcon }
