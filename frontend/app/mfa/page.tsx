'use client'

import { QRCode } from '@/components/shared-assets/qr-code'
import { ArrowRightIcon, type ArrowRightIconHandle } from '@/components/ui/arrow-right'
import { Button } from '@/components/ui/button'
import { getApiBaseUrl } from '@/lib/api'
import { PageBackground, DotMetersRow } from '@/lib/page-layouts'
import { useRouter } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'
import { playSound } from '@/lib/sound-engine'
import { switch001Sound } from '@/lib/switch-001'

type MFASetupResponse = {
  provisioning_uri: string
  mfa_enabled: boolean
}
const buttonIconSize = 22
const buttonIconStrokeWidth = 3.0

export default function MultiFactorAuthentication() {
  const handlePlay = () => {
    void playSound(switch001Sound.dataUri)
  }

  const router = useRouter()
  const setupRequested = useRef(false)
  const arrowRightIconRef = useRef<ArrowRightIconHandle>(null)
  const [setupUri, setSetupUri] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (setupRequested.current) {
      return
    }

    setupRequested.current = true

    const abortController = new AbortController()

    const loadMfaSetup = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`${getApiBaseUrl()}/auth/mfa/setup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          signal: abortController.signal,
        })

        const payload = await response.json()

        if (!response.ok) {
          throw new Error(payload?.detail || payload?.message || 'MFA setup failed.')
        }

        setSetupUri((payload as MFASetupResponse).provisioning_uri)
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          return
        }
        const message = err instanceof Error ? err.message : 'The MFA Setup Failed.'
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    void loadMfaSetup()

    return () => {
      abortController.abort()
    }
  }, [])

  useEffect(() => {
    const startButtonIconAnimation = () => {
      arrowRightIconRef.current?.startAnimation()
    }

    const animationFrameId = window.requestAnimationFrame(startButtonIconAnimation)
    const intervalId = window.setInterval(() => {
      startButtonIconAnimation()
    }, 1200)

    return () => {
      window.cancelAnimationFrame(animationFrameId)
      window.clearInterval(intervalId)
    }
  }, [])

  return (
    <main className="relative min-h-svh overflow-hidden">
      <PageBackground />
      <section className="relative z-10 flex min-h-svh items-center justify-center px-4 py-8 sm:p-10">
        <div className="flex w-full max-w-lg flex-col items-center justify-center border border-gray-200/20 bg-[#000000] px-5 py-8 text-center sm:px-2.5 sm:py-10">
          <h3
            className="mb-5 text-lg font-extrabold text-gray-200 sm:text-xl"
            aria-label="Welcome To Vocalis"
          >
            Welcome To Vocalis
          </h3>
          <p
            className="max-w-sm text-sm font-semibold mb-10 leading-6 text-gray-300 sm:max-w-none sm:text-base"
            aria-label="Your Adaptive Explainable AI Pronunciation Training Companion"
          >
            Let&apos;s Authenticate And Verify Your Personal Vocalis Account
          </p>
          <div className="flex w-full flex-col items-center">
            <span className="mb-3 text-xs font-bold capitalize tracking-[0.15em] text-gray-500">
              Step 1 Of 2
            </span>
            <div className="flex min-h-[232px] items-center justify-center">
              {loading ? (
                <span className="text-sm font-semibold text-gray-400">Preparing MFA...</span>
              ) : setupUri ? (
                <QRCode value={setupUri} size="xl" />
              ) : (
                <span className="max-w-xs text-sm font-semibold text-gray-400">
                  Unable To Load The MFA QR Code.
                </span>
              )}
            </div>
            <p className="mt-5 max-w-xs text-xs font-semibold leading-5 text-gray-400 sm:text-sm">
              Scan This QR Code Using Your Preffered Authentication Application
            </p>

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
                disabled={loading || !setupUri}
                onClick={() => {
                  handlePlay()
                  router.push('/mfa/verify?mode=setup')
                }}
              >
                <ArrowRightIcon
                  ref={arrowRightIconRef}
                  data-icon="inline"
                  size={buttonIconSize}
                  strokeWidth={buttonIconStrokeWidth}
                />
                Continue
              </Button>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
