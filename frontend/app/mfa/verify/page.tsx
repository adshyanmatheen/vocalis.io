'use client'

import { ArrowLeftIcon, type ArrowLeftIconHandle } from '@/components/ui/arrow-left'
import { Button } from '@/components/ui/button'
import { ShieldCheckIcon, type ShieldCheckIconHandle } from '@/components/ui/shield-check'
import { InputOTP, InputOTPGroup, InputOTPSeparator, InputOTPSlot } from '@/components/ui/input-otp'
import { clickSoftSound } from '@/lib/click-soft'
import { error005Sound } from '@/lib/error-005'
import { getApiBaseUrl } from '@/lib/api'
import { PageBackground, DotMetersRow } from '@/lib/page-layouts'
import { playSound } from '@/lib/sound-engine'
import { successChimeSound } from '@/lib/success-chime'
import { switch001Sound } from '@/lib/switch-001'
import { motion, useReducedMotion, type Variants } from 'motion/react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
const buttonIconSize = 24
const buttonIconStrokeWidth = 2.35

export default function MFAVerification() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const prefersReducedMotion = useReducedMotion()
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const arrowLeftIconRef = useRef<ArrowLeftIconHandle>(null)
  const shieldCheckIconRef = useRef<ShieldCheckIconHandle>(null)
  const lastAutoSubmittedCode = useRef<string | null>(null)
  const verificationMode = searchParams.get('mode') === 'login' ? 'login' : 'setup'

  const handleBackNavigationSound = () => {
    void playSound(switch001Sound.dataUri)
  }

  const handleCodeChange = useCallback(
    (nextCode: string) => {
      if (nextCode !== code) {
        void playSound(clickSoftSound.dataUri, { volume: 0.8 })
      }
      setCode(nextCode)
    },
    [code],
  )

  const handleVerify = useCallback(async () => {
    const trimmedCode = code.trim()
    if (trimmedCode.length !== 6) {
      setError('Please Enter The Six Digit Code.')
      void playSound(error005Sound.dataUri, { volume: 0.8 })
      return
    }

    setLoading(true)
    setError(null)

    try {
      const request =
        verificationMode === 'login'
          ? {
              endpoint: '/auth/mfa/login',
              body: {
                temporary_token: sessionStorage.getItem('vocalis_mfa_temporary_token'),
                code: trimmedCode,
              },
            }
          : {
              endpoint: '/auth/mfa/verify',
              body: {
                code: trimmedCode,
              },
            }

      if (verificationMode === 'login' && !request.body.temporary_token) {
        throw new Error('The MFA Session Is Missing. Please Sign In Again.')
      }

      const response = await fetch(`${getApiBaseUrl()}${request.endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(request.body),
      })

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload?.detail || payload?.message || 'MFA verification failed.')
      }

      sessionStorage.removeItem('vocalis_mfa_temporary_token')
      await playSound(successChimeSound.dataUri, { volume: 0.8 })
      router.push('/home')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'The MFA Verification Failed.'
      setError(message)
      void playSound(error005Sound.dataUri, { volume: 0.8 })
    } finally {
      setLoading(false)
    }
  }, [code, router, verificationMode])

  useEffect(() => {
    if (loading || code.length !== 6) {
      if (code.length !== 6) {
        lastAutoSubmittedCode.current = null
      }
      return
    }
    if (lastAutoSubmittedCode.current === code) {
      return
    }
    lastAutoSubmittedCode.current = code
    void handleVerify()
  }, [code, handleVerify, loading])

  useEffect(() => {
    const startButtonIconAnimations = () => {
      arrowLeftIconRef.current?.startAnimation()
      shieldCheckIconRef.current?.startAnimation()
    }

    const animationFrameId = window.requestAnimationFrame(startButtonIconAnimations)
    const intervalId = window.setInterval(() => {
      startButtonIconAnimations()
    }, 1200)

    return () => {
      window.cancelAnimationFrame(animationFrameId)
      window.clearInterval(intervalId)
    }
  }, [])

  const controlVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : -8,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          delay: prefersReducedMotion ? 0 : 0.18,
          duration: prefersReducedMotion ? 0.01 : 0.48,
          ease: [0.22, 1, 0.36, 1],
        },
      },
    }),
    [prefersReducedMotion],
  )

  return (
    <main className="relative min-h-svh overflow-hidden">
      <PageBackground />

      <Link
        href="/mfa"
        aria-label="Back To MFA Setup"
        className="fixed left-4 top-4 z-20 size-12 outline-none sm:left-10 sm:top-10 sm:size-14"
        onClick={handleBackNavigationSound}
      >
        <motion.div
          className="flex size-full items-center justify-center border border-gray-200/20 bg-[#000000] text-gray-200 transition-colors hover:border-gray-200/35 focus-visible:border-gray-200/45"
          initial="hidden"
          animate="visible"
          variants={controlVariants}
          whileHover={prefersReducedMotion ? undefined : { scale: 1.04 }}
          whileTap={prefersReducedMotion ? undefined : { scale: 1.09 }}
          transition={{ type: 'spring', stiffness: 520, damping: 22, mass: 0.55 }}
        >
          <ArrowLeftIcon ref={arrowLeftIconRef} size={22} aria-hidden="true" />
        </motion.div>
      </Link>

      <section className="relative z-10 flex min-h-svh items-center justify-center px-4 py-8 sm:p-10">
        <div className="flex w-full max-w-lg flex-col items-center justify-center border border-gray-200/20 bg-[#000000] px-5 py-8 text-center sm:px-2.5 sm:py-10">
          <h3
            className="mb-5 text-lg font-extrabold text-gray-200 sm:text-xl"
            aria-label="Verify Vocalis MFA"
          >
            Welcome To Vocalis
          </h3>
          <p className="mb-10 max-w-sm text-sm font-semibold leading-6 text-gray-300 sm:max-w-none sm:text-base">
            Let&apos;s Authenticate And Verify Your Personal Vocalis Account
          </p>
          <span className="mb-7 text-xs font-bold capitalize tracking-[0.15em] text-gray-500">
            Step 2 Of 2
          </span>
          <div className="flex w-full flex-col items-center">
            <InputOTP
              maxLength={6}
              value={code}
              onChange={handleCodeChange}
              containerClassName="justify-center"
            >
              <InputOTPGroup className="gap-2 sm:gap-3">
                {Array.from({ length: 3 }).map((_, index) => (
                  <InputOTPSlot
                    key={index}
                    index={index}
                    className="size-12 border border-gray-500 bg-transparent text-lg font-semibold text-gray-100 data-[active=true]:border-gray-200 sm:size-15 sm:text-xl"
                  />
                ))}
                <InputOTPSeparator className="text-gray-500" />
                {Array.from({ length: 3 }).map((_, index) => {
                  const slotIndex = index + 3

                  return (
                    <InputOTPSlot
                      key={slotIndex}
                      index={slotIndex}
                      className="size-12 border border-gray-500 bg-transparent text-lg font-semibold text-gray-100 data-[active=true]:border-gray-200 sm:size-15 sm:text-xl"
                    />
                  )
                })}
              </InputOTPGroup>
            </InputOTP>
            <p className="mt-7 max-w-sm text-xs font-semibold leading-5 text-gray-400 sm:text-sm">
              Enter The Six Digit Code From Your Preffered Authentication Application
            </p>
          </div>

          {error ? (
            <div
              className="mt-4 px-5 text-left text-sm text-red-400"
              role="alert"
              aria-live="polite"
            >
              {error}
            </div>
          ) : null}

          <DotMetersRow />

          <div className="mt-8 flex w-full items-center justify-center gap-2 sm:w-auto">
            <Button
              size="lg"
              type="button"
              className="w-full max-w-52 font-bold capitalize text-md sm:w-auto"
              disabled={code.length !== 6 || loading}
              onClick={handleVerify}
            >
              <ShieldCheckIcon
                ref={shieldCheckIconRef}
                data-icon="inline-start"
                size={buttonIconSize}
                strokeWidth={buttonIconStrokeWidth}
              />
              {loading ? 'Verifying...' : 'Verify'}
            </Button>
          </div>
        </div>
      </section>
    </main>
  )
}
