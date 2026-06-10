'use client'

import CountUp from '@/components/CountUp'
import DotField from '@/components/DotField'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ArrowLeftIcon, type ArrowLeftIconHandle } from '@/components/ui/arrow-left'
import { Button } from '@/components/ui/button'
import { DotmSquare18 } from '@/components/ui/dotm-square-18'
import { LogoutIcon, type LogoutIconHandle } from '@/components/ui/logout'
import { fetchAccountSummary, logoutUser, type AccountSummary } from '@/lib/api'
import { question004Sound } from '@/lib/question-004'
import { playSound } from '@/lib/sound-engine'
import { switch001Sound } from '@/lib/switch-001'
import { useRequireAuth } from '@/lib/use-require-auth'
import { motion, useReducedMotion, type Variants } from 'motion/react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

const dotMeters = Array.from({ length: 8 })

const handlePlay = () => {
  void playSound(switch001Sound.dataUri)
}

const getUserInitials = (name: string | undefined) => {
  if (!name?.trim()) {
    return 'V'
  }

  return (
    name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase() || 'V'
  )
}

const getScorePercent = (score: number | undefined) => {
  if (typeof score !== 'number' || Number.isNaN(score)) {
    return 0
  }

  const normalizedScore = score > 1 ? score / 100 : score
  return Math.round(Math.max(0, Math.min(1, normalizedScore)) * 100)
}

const formatScore = (score: number | undefined) => `${getScorePercent(score)}%`

export default function Account() {
  const router = useRouter()
  const prefersReducedMotion = useReducedMotion()
  const arrowLeftIconRef = useRef<ArrowLeftIconHandle>(null)
  const logoutIconRef = useRef<LogoutIconHandle>(null)
  const { user, loading } = useRequireAuth()
  const [summary, setSummary] = useState<AccountSummary | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(true)
  const [logoutLoading, setLogoutLoading] = useState(false)

  const containerVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 8,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.56,
          ease: [0.22, 1, 0.36, 1],
          staggerChildren: prefersReducedMotion ? 0 : 0.05,
        },
      },
    }),
    [prefersReducedMotion],
  )

  const itemVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 8,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.44,
          ease: [0.22, 1, 0.36, 1],
        },
      },
    }),
    [prefersReducedMotion],
  )

  const rowContainerVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: 1,
      },
      visible: {
        opacity: 1,
        transition: {
          delayChildren: prefersReducedMotion ? 0 : 0.1,
          staggerChildren: prefersReducedMotion ? 0 : 0.11,
        },
      },
    }),
    [prefersReducedMotion],
  )

  const sectionVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 26,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.58,
          ease: [0.22, 1, 0.36, 1],
          delayChildren: prefersReducedMotion ? 0 : 0.08,
          staggerChildren: prefersReducedMotion ? 0 : 0.08,
        },
      },
    }),
    [prefersReducedMotion],
  )

  const rowVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 18,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.48,
          ease: [0.22, 1, 0.36, 1],
        },
      },
    }),
    [prefersReducedMotion],
  )

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

  const displayUser = summary?.user ?? user
  const stats = useMemo(
    () => [
      {
        label: 'Attempts',
        value: summary?.activity.total_attempts ?? 0,
        suffix: '',
      },
      {
        label: 'Average',
        value: getScorePercent(summary?.activity.average_score),
        suffix: '%',
      },
      {
        label: 'Best',
        value: getScorePercent(summary?.activity.best_score),
        suffix: '%',
      },
      {
        label: 'Latest',
        value: getScorePercent(summary?.activity.latest_score),
        suffix: '%',
      },
    ],
    [summary],
  )

  const focusRows = summary?.personalization.focus_phonemes.slice(0, 4) ?? []
  const attemptRows = summary?.activity.recent_attempts.slice(0, 4) ?? []

  const loadSummary = useCallback(async (signal?: AbortSignal) => {
    setSummaryLoading(true)
    setErrorMessage(null)

    try {
      setSummary(await fetchAccountSummary(signal))
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        return
      }
      setErrorMessage(error instanceof Error ? error.message : 'Unable to load account summary.')
    } finally {
      if (!signal?.aborted) {
        setSummaryLoading(false)
      }
    }
  }, [])

  const abortControllerRef = useRef<AbortController | null>(null)

  const handleLogout = useCallback(async () => {
    setLogoutLoading(true)
    void playSound(question004Sound.dataUri)

    try {
      await logoutUser()
    } catch {
      // Logout failed, but still redirect
    } finally {
      router.replace('/sign-in')
      setLogoutLoading(false)
    }
  }, [router])

  useEffect(() => {
    if (!loading && user) {
      abortControllerRef.current?.abort()
      const controller = new AbortController()
      abortControllerRef.current = controller

      const timeoutId = window.setTimeout(() => {
        void loadSummary(controller.signal)
      }, 0)

      return () => {
        window.clearTimeout(timeoutId)
        controller.abort()
      }
    }
  }, [loadSummary, loading, user])

  useEffect(() => {
    if (prefersReducedMotion) {
      return
    }

    const arrowLeftIcon = arrowLeftIconRef.current
    const logoutIcon = logoutIconRef.current

    arrowLeftIcon?.startAnimation()
    logoutIcon?.startAnimation()
    const intervalId = window.setInterval(() => {
      arrowLeftIcon?.startAnimation()
      logoutIcon?.startAnimation()
    }, 1200)

    return () => {
      window.clearInterval(intervalId)
    }
  }, [prefersReducedMotion])

  return (
    <main className="relative min-h-svh overflow-hidden">
      <div className="fixed inset-0 -z-10">
        <DotField
          dotRadius={1.0}
          dotSpacing={22}
          cursorRadius={200}
          cursorForce={0}
          bulgeOnly={false}
          bulgeStrength={0}
          glowRadius={210}
          sparkle
          waveAmplitude={0}
          gradientFrom="#cbcbcb"
          gradientTo="#cbcbcb"
        />
      </div>

      <Link
        href="/home"
        aria-label="Back To Home"
        className="fixed left-4 top-4 z-20 size-12 outline-none sm:left-10 sm:top-10 sm:size-14"
        onClick={handlePlay}
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

      <section className="relative z-10 box-border min-h-svh px-4 py-24 sm:px-10 sm:py-28">
        <div className="mx-auto flex w-full max-w-xl flex-col gap-8">
          <motion.div
            className="flex w-full flex-col items-center justify-center border border-gray-200/20 bg-[#000000] px-5 py-8 text-center sm:px-10 sm:py-10"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
          >
            <motion.h3
              className="mb-3 text-lg font-extrabold text-gray-200 sm:text-xl"
              variants={itemVariants}
            >
              Welcome To Your Personal Vocalis Account
            </motion.h3>
            <motion.p
              className="mb-8 max-w-md text-sm font-semibold leading-6 text-gray-400 capitalize sm:text-base"
              variants={itemVariants}
            >
              Here&apos;s a snapshot of your Activities And Attempts
            </motion.p>

            <motion.div className="flex flex-col items-center" variants={itemVariants}>
              <Avatar className="size-24 overflow-hidden rounded-full bg-black ring-1 ring-white/10 sm:size-28">
                {displayUser?.avatar_url ? (
                  <AvatarImage
                    className="scale-[1.02] rounded-full"
                    src={displayUser.avatar_url}
                    alt={
                      displayUser.name ? `${displayUser.name} profile picture` : 'Profile picture'
                    }
                  />
                ) : null}
                <AvatarFallback className="rounded-full bg-white text-xl font-bold text-black">
                  {getUserInitials(displayUser?.name)}
                </AvatarFallback>
              </Avatar>

              <h1 className="mt-5 max-w-full truncate text-3xl font-extrabold text-gray-100 sm:text-4xl">
                {displayUser?.name ?? 'Account'}
              </h1>
              <p className="mt-2 max-w-full truncate text-sm font-semibold text-gray-400">
                @{displayUser?.username ?? 'vocalis'}
              </p>
            </motion.div>

            {errorMessage ? (
              <motion.p className="mt-5 text-sm font-semibold text-red-400" variants={itemVariants}>
                {errorMessage}
              </motion.p>
            ) : null}

            <motion.div
              className="mt-10 grid w-full grid-cols-2 border border-gray-200/15"
              variants={itemVariants}
            >
              {stats.map((stat, index) => (
                <div
                  key={stat.label}
                  className={`px-3 py-5 ${index % 2 === 0 ? 'border-r border-gray-200/10' : ''} ${index < 2 ? 'border-b border-gray-200/10' : ''}`}
                >
                  <p className="text-[11px] font-bold capitalize text-gray-500">{stat.label}</p>
                  <p className="mt-2 text-3xl font-extrabold text-gray-100 sm:text-4xl">
                    {summaryLoading ? (
                      '--'
                    ) : (
                      <>
                        <CountUp to={stat.value} duration={1.1} />
                        {stat.suffix}
                      </>
                    )}
                  </p>
                </div>
              ))}
            </motion.div>

            <motion.div
              className="mt-8 flex items-center justify-center gap-1.5 sm:hidden"
              variants={itemVariants}
            >
              {dotMeters.map((_, i) => (
                <DotmSquare18
                  key={i}
                  size={35}
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
            </motion.div>
            <motion.div
              className="mt-15 hidden items-center justify-center gap-2 sm:flex"
              variants={itemVariants}
            >
              {dotMeters.map((_, i) => (
                <DotmSquare18
                  key={i}
                  size={52}
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
            </motion.div>

            <motion.div
              className="mt-10 flex w-full items-center justify-center gap-2 sm:w-auto"
              variants={itemVariants}
            >
              <Button
                size="lg"
                type="button"
                className="w-full max-w-52 bg-white font-bold normal-case capitalize text-md text-black hover:bg-red-500 hover:text-white sm:w-auto"
                disabled={logoutLoading}
                onClick={handleLogout}
              >
                <LogoutIcon
                  ref={logoutIconRef}
                  size={23}
                  className="[&_svg]:stroke-[2.7]"
                  aria-hidden="true"
                />
                {logoutLoading ? 'Signing Out...' : 'Sign Out'}
              </Button>
            </motion.div>
          </motion.div>

          <motion.section
            className="w-full border border-gray-200/20 bg-[#000000]"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.18, margin: '0px 0px -12% 0px' }}
            variants={sectionVariants}
          >
            <motion.div
              className="border-b border-gray-200/15 px-5 py-5 text-center sm:px-8"
              variants={itemVariants}
            >
              <h2 className="text-base font-extrabold text-gray-200 sm:text-lg">
                Your Personal Focus Sounds
              </h2>
              <p className="mt-2 text-sm font-semibold leading-6 text-gray-400">
                {summary?.personalization.recurring_sound_note ?? ''}
              </p>
            </motion.div>

            <motion.div className="max-h-80 overflow-y-auto" variants={rowContainerVariants}>
              {focusRows.length ? (
                focusRows.map((focus, index) => (
                  <motion.div
                    key={focus.phoneme}
                    className="grid min-h-24 grid-cols-[84px_1fr] border-b border-gray-200/15 last:border-b-0 sm:grid-cols-[112px_1fr]"
                    variants={rowVariants}
                  >
                    <div className="flex items-center justify-center border-r border-gray-200/15 px-3">
                      <p className="font-mono text-2xl font-extrabold text-gray-100 sm:text-3xl">
                        {String(index + 1).padStart(2, '0')}
                      </p>
                    </div>
                    <div className="flex flex-col items-center justify-center px-5 py-5 text-center">
                      <p className="text-base font-semibold leading-7 text-gray-300 sm:text-lg">
                        Train /{focus.phoneme}/ with slow, careful repetitions.
                      </p>
                      <p className="mt-2 text-xs font-bold capitalize text-gray-500">
                        {formatScore(focus.average_score)} average · {focus.weak_occurrences} weak
                        occurrences
                      </p>
                    </div>
                  </motion.div>
                ))
              ) : (
                <motion.div
                  className="flex min-h-24 items-center justify-center px-5 py-6 text-center"
                  variants={rowVariants}
                >
                  <p className="text-base font-semibold leading-7 text-gray-400 sm:text-md capitalize">
                    No recurring focus sounds yet
                  </p>
                </motion.div>
              )}
            </motion.div>
          </motion.section>

          <motion.section
            className="w-full border border-gray-200/20 bg-[#000000]"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.16, margin: '0px 0px -12% 0px' }}
            variants={sectionVariants}
          >
            <motion.div
              className="border-b border-gray-200/15 px-5 py-5 text-center sm:px-8"
              variants={itemVariants}
            >
              <h2 className="text-base font-extrabold text-gray-200 sm:text-lg">
                Your Recent Pronunciation Attempts
              </h2>
            </motion.div>

            <motion.div className="overflow-hidden" variants={rowContainerVariants}>
              {attemptRows.length ? (
                attemptRows.map((attempt, index) => (
                  <motion.div
                    key={attempt.id}
                    className="grid min-h-28 grid-cols-[84px_1fr] border-b border-gray-200/15 last:border-b-0 sm:grid-cols-[112px_1fr_110px]"
                    variants={rowVariants}
                  >
                    <div className="flex items-center justify-center border-r border-gray-200/15 px-3">
                      <p className="font-mono text-2xl font-extrabold text-gray-100 sm:text-3xl">
                        {String(index + 1).padStart(2, '0')}
                      </p>
                    </div>
                    <div className="flex flex-col items-center justify-center px-5 py-5 text-center">
                      <p className="text-base font-semibold leading-7 text-gray-300 capitalize sm:text-lg">
                        {attempt.target_text}
                      </p>
                      <p className="mt-2 text-xs font-bold capitalize text-gray-500">
                        {attempt.performance_band}
                      </p>
                    </div>
                    <div className="flex items-center justify-center border-t border-gray-200/15 px-4 py-4 sm:border-l sm:border-t-0">
                      <p className="text-2xl font-extrabold text-gray-100">
                        {formatScore(attempt.overall_score)}
                      </p>
                    </div>
                  </motion.div>
                ))
              ) : (
                <motion.div
                  className="flex min-h-24 items-center justify-center px-5 py-5 text-center"
                  variants={rowVariants}
                >
                  <p className="text-base font-semibold leading-7 text-gray-400 capitalize sm:text-md">
                    Your practice history will appear here
                  </p>
                </motion.div>
              )}
            </motion.div>
          </motion.section>
        </div>
      </section>
    </main>
  )
}
