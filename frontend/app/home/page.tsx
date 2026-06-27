'use client'

import CountUp from '@/components/CountUp'
import { PageBackground } from '@/lib/page-layouts'
import {
  AudioPlayer,
  AudioPlayerControlBar,
  AudioPlayerDurationDisplay,
  AudioPlayerElement,
  AudioPlayerPlayButton,
  AudioPlayerTimeDisplay,
  AudioPlayerTimeRange,
  AudioPlayerVolumeRange,
} from '@/components/ai-elements/audio-player'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { DotmSquare18 } from '@/components/ui/dotm-square-18'
import { AudioLinesIcon, type AudioLinesIconHandle } from '@/components/ui/audio-lines'
import { preprocessRecordedAudio, type PreprocessedAudio } from '@/lib/audio/preprocess'
import { GripIcon, type GripIconHandle } from '@/components/ui/grip'
import { useRequireAuth } from '@/lib/use-require-auth'
import {
  getModelHealth,
  getModelHealthMessage,
  submitRealtimeAssessment,
  type AssessmentCompletedEvent,
} from '@/lib/realtime-assessment'
import {
  dotMeters,
  formatMetricNumber,
  formatScore,
  getOverallScorePercent,
  getTimeBasedGreeting,
  getUserInitials,
  getWeakPhonemeTier,
  getWordScoreLabel,
  getWordScoreValue,
  MAX_WEAK_PHONEMES_DISPLAYED,
  type VoiceState,
} from '@/lib/home-assessment'
import { useAttemptHistory, type AttemptSnapshot } from '@/lib/use-attempt-history'
import { useEnrichedAssessmentResult } from '@/lib/use-enriched-assessment-result'
import { useTargetText } from '@/lib/use-target-text'
import { cn } from '@/lib/utils'
import { AnimatePresence, motion, useReducedMotion, type Variants } from 'motion/react'
import Link from 'next/link'
import { error005Sound } from '@/lib/error-005'
import { playSound } from '@/lib/sound-engine'
import { successChimeSound } from '@/lib/success-chime'
import { switch001Sound } from '@/lib/switch-001'
import { switchOffSound } from '@/lib/switch-off'
import { switchOnSound } from '@/lib/switch-on'
import { logger } from '@/lib/logger'
import { useCallback, useEffect, useMemo, useRef, useState, type SyntheticEvent } from 'react'

const handlePlay = () => {
  void playSound(switch001Sound.dataUri)
}

const playSuccessChime = () => {
  void playSound(successChimeSound.dataUri)
}

const playErrorChime = () => {
  void playSound(error005Sound.dataUri)
}

export default function Home() {
  const { user, loading } = useRequireAuth()
  const { targetText, loadTargetText } = useTargetText()
  const [greeting] = useState(getTimeBasedGreeting)
  const [voiceState, setVoiceState] = useState<VoiceState>('idle')
  const [audioIssues, setAudioIssues] = useState<string[]>([])
  const [preprocessedAudio, setPreprocessedAudio] = useState<PreprocessedAudio | null>(null)
  const [assessmentResult, setAssessmentResult] = useState<AssessmentCompletedEvent | null>(null)
  const { attemptHistory, appendAttempt } = useAttemptHistory()
  const [showAdvancedDetails, setShowAdvancedDetails] = useState(false)
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string | null>(null)
  const audioLinesIconRef = useRef<AudioLinesIconHandle>(null)
  const gripIconRef = useRef<GripIconHandle>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const recordingLockRef = useRef(false)
  const healthCheckAbortRef = useRef<AbortController | null>(null)
  const wasRecordedAudioPlayingRef = useRef(false)
  const prefersReducedMotion = useReducedMotion()
  const isRecordingStartup = voiceState === 'preparing' || voiceState === 'recording'
  const isProcessingAudio = voiceState === 'preprocessing' || voiceState === 'submitting'
  const isVoiceActionDisabled =
    voiceState === 'preparing' || voiceState === 'preprocessing' || voiceState === 'submitting'
  const resultViewport = useMemo(() => ({ once: true, amount: 0.2 }), [])
  const resultSectionVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 18,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.55,
          ease: [0.22, 1, 0.36, 1],
        },
      },
    }),
    [prefersReducedMotion],
  )
  const resultListVariants = useMemo<Variants>(
    () => ({
      hidden: {},
      visible: {
        transition: {
          delayChildren: prefersReducedMotion ? 0 : 0.04,
          staggerChildren: prefersReducedMotion ? 0 : 0.065,
        },
      },
    }),
    [prefersReducedMotion],
  )
  const resultItemVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 10,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.42,
          ease: [0.22, 1, 0.36, 1],
        },
      },
    }),
    [prefersReducedMotion],
  )
  const topContainerVariants = useMemo<Variants>(
    () => ({
      hidden: {},
      visible: {
        transition: {
          staggerChildren: prefersReducedMotion ? 0 : 0.075,
          delayChildren: prefersReducedMotion ? 0 : 0.08,
        },
      },
    }),
    [prefersReducedMotion],
  )
  const topItemVariants = useMemo<Variants>(
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
        },
      },
    }),
    [prefersReducedMotion],
  )
  const topMeterVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 10,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.58,
          ease: [0.22, 1, 0.36, 1],
        },
      },
    }),
    [prefersReducedMotion],
  )
  const targetTextVariants = useMemo<Variants>(
    () => ({
      hidden: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : 8,
      },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.42,
          ease: [0.22, 1, 0.36, 1],
        },
      },
      exit: {
        opacity: prefersReducedMotion ? 1 : 0,
        y: prefersReducedMotion ? 0 : -6,
        transition: {
          duration: prefersReducedMotion ? 0.01 : 0.2,
          ease: [0.4, 0, 1, 1],
        },
      },
    }),
    [prefersReducedMotion],
  )
  const accountContainerVariants = useMemo<Variants>(
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

  const enrichedResult = useEnrichedAssessmentResult(assessmentResult, attemptHistory)

  const stopMediaStream = useCallback(() => {
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop())
    mediaStreamRef.current = null
  }, [])

  const ensureAssessmentEngineReady = useCallback(async () => {
    healthCheckAbortRef.current?.abort()
    const controller = new AbortController()
    healthCheckAbortRef.current = controller

    try {
      const modelHealth = await getModelHealth(controller.signal)
      const readinessMessage = getModelHealthMessage(modelHealth)

      if (readinessMessage) {
        setAudioIssues([readinessMessage])
        setVoiceState('error')
        return false
      }

      return true
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        return false
      }
      throw error
    }
  }, [])

  const processRecording = useCallback(
    async (audioBlob: Blob) => {
      try {
        setVoiceState('preprocessing')
        const result = await preprocessRecordedAudio(audioBlob)
        const nextPreprocessedAudio = result.wavBlob ? (result as PreprocessedAudio) : null

        setPreprocessedAudio(nextPreprocessedAudio)
        setAudioIssues(result.issues)
        if (nextPreprocessedAudio?.wavBlob) {
          setRecordedAudioUrl((previousUrl) => {
            if (previousUrl) {
              URL.revokeObjectURL(previousUrl)
            }
            return URL.createObjectURL(nextPreprocessedAudio.wavBlob)
          })
        }

        if (result.issues.length > 0 || !nextPreprocessedAudio?.trimmedBuffer) {
          playErrorChime()
          setVoiceState('error')
          return
        }

        if (!(await ensureAssessmentEngineReady())) {
          playErrorChime()
          return
        }

        setVoiceState('submitting')
        const assessment = await submitRealtimeAssessment({
          targetText,
          audioBuffer: nextPreprocessedAudio.trimmedBuffer,
        })

        setAssessmentResult(assessment)
        await loadTargetText(
          assessment.feedback.highlights?.next_focus?.length
            ? assessment.feedback.highlights.next_focus
            : assessment.weak_phonemes,
        )
        playSuccessChime()
        setVoiceState('completed')
      } catch (error) {
        logger.error('Assessment submission failed:', error)
        setAssessmentResult(null)
        setAudioIssues([
          error instanceof Error ? error.message : 'The Audio Assessment Failed. Please Try Again.',
        ])
        playErrorChime()
        setVoiceState('error')
      }
    },
    [ensureAssessmentEngineReady, loadTargetText, targetText],
  )

  const handleRecordedAudioPlay = useCallback(() => {
    wasRecordedAudioPlayingRef.current = true
    void playSound(switchOnSound.dataUri)
  }, [])

  const handleRecordedAudioPause = useCallback((event: SyntheticEvent<HTMLAudioElement>) => {
    if (!wasRecordedAudioPlayingRef.current) {
      return
    }

    wasRecordedAudioPlayingRef.current = false

    if (!event.currentTarget.ended) {
      void playSound(switchOffSound.dataUri)
    }
  }, [])

  const handleRecordedAudioEnded = useCallback(() => {
    wasRecordedAudioPlayingRef.current = false
  }, [])

  const startRecording = useCallback(async () => {
    if (recordingLockRef.current) {
      return
    }

    recordingLockRef.current = true

    try {
      setVoiceState('preparing')
      setAudioIssues([])
      setPreprocessedAudio(null)
      setAssessmentResult(null)
      audioChunksRef.current = []
      setRecordedAudioUrl((previousUrl) => {
        if (previousUrl) {
          URL.revokeObjectURL(previousUrl)
        }
        return null
      })

      if (!(await ensureAssessmentEngineReady())) {
        return
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })

      mediaStreamRef.current = stream
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.addEventListener('dataavailable', (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      })

      mediaRecorder.addEventListener(
        'stop',
        () => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: mediaRecorder.mimeType || 'audio/webm',
          })

          stopMediaStream()
          void processRecording(audioBlob)
        },
        { once: true },
      )

      mediaRecorder.start()
      recordingLockRef.current = false
      setVoiceState('recording')
    } catch (error) {
      recordingLockRef.current = false
      logger.error('Microphone access failed:', error)
      stopMediaStream()
      setAudioIssues(['Microphone access failed. Please allow microphone access and try again.'])
      setVoiceState('error')
    }
  }, [ensureAssessmentEngineReady, processRecording, stopMediaStream])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop()
      return
    }

    stopMediaStream()
    setVoiceState('preprocessing')
  }, [stopMediaStream])

  const handleVoicePress = useCallback(() => {
    if (voiceState === 'idle' || voiceState === 'completed' || voiceState === 'error') {
      handlePlay()
      void startRecording()
      return
    }

    if (voiceState === 'recording') {
      handlePlay()
      stopRecording()
    }
  }, [startRecording, stopRecording, voiceState])

  const cycleTargetText = useCallback(async () => {
    if (
      voiceState === 'preparing' ||
      voiceState === 'recording' ||
      voiceState === 'preprocessing' ||
      voiceState === 'submitting'
    ) {
      return
    }

    setAudioIssues([])
    setPreprocessedAudio(null)
    setAssessmentResult(null)
    setRecordedAudioUrl((previousUrl) => {
      if (previousUrl) {
        URL.revokeObjectURL(previousUrl)
      }
      return null
    })
    await loadTargetText()
    setVoiceState('idle')
  }, [loadTargetText, voiceState])

  useEffect(() => {
    let animationFrameId = 0

    const runAfterMount = (callback: () => void) => {
      animationFrameId = window.requestAnimationFrame(callback)
    }

    if (isRecordingStartup) {
      runAfterMount(() => {
        audioLinesIconRef.current?.startAnimation()
      })
      return () => {
        window.cancelAnimationFrame(animationFrameId)
      }
    }

    runAfterMount(() => {
      audioLinesIconRef.current?.stopAnimation()
    })

    return () => {
      window.cancelAnimationFrame(animationFrameId)
    }
  }, [isRecordingStartup])

  useEffect(() => {
    if (!isProcessingAudio || prefersReducedMotion) {
      return
    }

    const animationFrameId = window.requestAnimationFrame(() => {
      gripIconRef.current?.startAnimation()
    })
    const intervalId = window.setInterval(() => {
      gripIconRef.current?.startAnimation()
    }, 900)

    return () => {
      window.cancelAnimationFrame(animationFrameId)
      window.clearInterval(intervalId)
    }
  }, [isProcessingAudio, prefersReducedMotion])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target
      const isTyping =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target instanceof HTMLSelectElement ||
        (target instanceof HTMLElement && target.isContentEditable)

      if (isTyping || event.repeat || event.metaKey || event.ctrlKey || event.altKey) {
        return
      }

      if (event.code === 'Space') {
        event.preventDefault()
        handleVoicePress()
        return
      }

      if (event.code === 'KeyN') {
        event.preventDefault()
        void cycleTargetText()
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [cycleTargetText, handleVoicePress])

  useEffect(() => {
    return () => {
      healthCheckAbortRef.current?.abort()
      if (mediaRecorderRef.current?.state === 'recording') {
        mediaRecorderRef.current.stop()
      }

      stopMediaStream()
    }
  }, [stopMediaStream])

  useEffect(() => {
    return () => {
      if (recordedAudioUrl) {
        URL.revokeObjectURL(recordedAudioUrl)
      }
    }
  }, [recordedAudioUrl])

  useEffect(() => {
    if (!assessmentResult) {
      return
    }
    const snapshot: AttemptSnapshot = {
      score: assessmentResult.overall_score,
      createdAt: new Date().toISOString(),
      weakCount: assessmentResult.weak_phonemes.length,
      durationSeconds:
        typeof assessmentResult.feedback.realtime?.duration_seconds === 'number'
          ? assessmentResult.feedback.realtime.duration_seconds
          : 0,
    }
    window.queueMicrotask(() => {
      appendAttempt(snapshot)
    })
  }, [appendAttempt, assessmentResult])

  useEffect(() => {
    window.queueMicrotask(() => {
      void loadTargetText()
    })
  }, [loadTargetText])

  return (
    <main className={cn('relative', assessmentResult ? 'min-h-svh' : 'h-svh overflow-hidden')}>
      <PageBackground />
      <Link
        href="/account"
        aria-label="Open account"
        className="fixed right-4 top-4 z-20 size-12 outline-none sm:right-10 sm:top-10 sm:size-14"
        onClick={handlePlay}
      >
        <motion.div
          className="size-full"
          initial="hidden"
          animate="visible"
          variants={accountContainerVariants}
        >
          <motion.div
            className="flex size-full items-center justify-center border border-gray-200/20 bg-[#000000] transition-colors hover:border-gray-200/35 focus-visible:border-gray-200/45"
            whileHover={prefersReducedMotion ? undefined : { scale: 1.04 }}
            whileTap={prefersReducedMotion ? undefined : { scale: 1.09 }}
            transition={{ type: 'spring', stiffness: 520, damping: 22, mass: 0.55 }}
          >
            <Avatar className="size-8 overflow-hidden rounded-full bg-black ring-1 ring-white/10 after:border-white/10 sm:size-9">
              {user?.avatar_url ? (
                <AvatarImage
                  className="scale-[1.02] rounded-full"
                  src={user.avatar_url}
                  alt={user.name ? `${user.name} profile picture` : 'Profile picture'}
                />
              ) : null}
              <AvatarFallback className="rounded-full bg-white text-xs font-bold text-black">
                {getUserInitials(user?.name)}
              </AvatarFallback>
            </Avatar>
          </motion.div>
        </motion.div>
      </Link>
      <section
        className={cn(
          'relative z-10 box-border px-4 py-8 sm:p-10',
          !assessmentResult && 'h-full overflow-hidden',
        )}
      >
        <div className="mx-auto h-full w-full max-w-xl">
          <div
            className={cn(
              'flex items-center justify-center',
              assessmentResult ? 'min-h-svh' : 'h-full',
            )}
          >
            <motion.div
              className="flex w-full flex-col items-center justify-center border border-gray-200/20 bg-[#000000] px-10 py-8 text-center sm:px-2.5 sm:py-10"
              initial="hidden"
              animate="visible"
              variants={topContainerVariants}
            >
              <motion.h3
                className="mb-5 text-lg font-extrabold text-gray-200 sm:text-xl"
                aria-label="Welcome Back To Vocalis"
                variants={topItemVariants}
              >
                {loading ? greeting : `${greeting} ${user?.name ?? 'To You'}`}
              </motion.h3>
              <motion.p
                className="max-w-sm text-sm font-semibold capitalize mb-5 leading-6 text-gray-300 sm:max-w-none sm:text-base"
                aria-label="Let's Practice Your Pronunciation Today"
                variants={topItemVariants}
              >
                Let&apos;s Practice Your Pronunciation Today, One Word at a Time
              </motion.p>
              <motion.section
                className="w-full max-w-xl px-6 text-left sm:px-10"
                aria-labelledby="target-text-heading"
                variants={topItemVariants}
              >
                <div className="mt-5 flex min-h-32 items-center justify-center sm:min-h-36">
                  <AnimatePresence mode="wait" initial={false}>
                    <motion.p
                      key={targetText}
                      className="text-center text-2xl capitalize break-words font-extrabold leading-8 text-gray-100 sm:text-3xl sm:leading-11"
                      initial="hidden"
                      animate="visible"
                      exit="exit"
                      variants={targetTextVariants}
                    >
                      {targetText}
                    </motion.p>
                  </AnimatePresence>
                </div>
              </motion.section>

              <motion.div
                className="mt-15 flex items-center justify-center gap-1.5 sm:hidden"
                variants={topMeterVariants}
              >
                {dotMeters.map((_, i) => (
                  <DotmSquare18
                    key={i}
                    size={31}
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
                className="mt-10 hidden items-center justify-center gap-2 sm:flex"
                variants={topMeterVariants}
              >
                {dotMeters.map((_, i) => (
                  <DotmSquare18
                    key={i}
                    size={48}
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
                className="mt-8 flex w-full items-center justify-center gap-2 sm:mt-10 sm:w-auto"
                variants={topItemVariants}
              >
                <motion.div
                  className="w-full max-w-52 sm:w-auto"
                  whileHover={
                    !prefersReducedMotion && !isVoiceActionDisabled ? { scale: 1.035 } : undefined
                  }
                  whileTap={
                    !prefersReducedMotion && !isVoiceActionDisabled ? { scale: 1.07 } : undefined
                  }
                  transition={{ type: 'spring', stiffness: 520, damping: 22, mass: 0.55 }}
                >
                  <Button
                    size="lg"
                    type="button"
                    className="w-full bg-white font-bold normal-case capitalize text-md text-black hover:bg-gray-200 sm:w-auto"
                    disabled={isVoiceActionDisabled}
                    aria-label={voiceState === 'recording' ? 'Stop recording' : 'Record audio'}
                    onClick={handleVoicePress}
                  >
                    {isProcessingAudio ? (
                      <GripIcon key="processing-icon" ref={gripIconRef} size={22} />
                    ) : (
                      <AudioLinesIcon
                        key={isRecordingStartup ? 'active-audio-icon' : 'ready-icon'}
                        ref={audioLinesIconRef}
                        size={22}
                      />
                    )}
                    {voiceState === 'recording'
                      ? 'Recording...'
                      : voiceState === 'preparing'
                        ? 'Preparing...'
                        : voiceState === 'preprocessing'
                          ? 'Processing...'
                          : voiceState === 'submitting'
                            ? 'Evaluating...'
                            : assessmentResult || preprocessedAudio
                              ? 'Record Again'
                              : 'Record Audio'}
                  </Button>
                </motion.div>
              </motion.div>
              {recordedAudioUrl ? (
                <motion.div
                  className="mt-10 w-full max-w-lg"
                  initial="hidden"
                  animate="visible"
                  variants={topItemVariants}
                >
                  <div>
                    <AudioPlayer className="w-full text-gray-200">
                      <AudioPlayerElement
                        src={recordedAudioUrl}
                        onPlay={handleRecordedAudioPlay}
                        onPause={handleRecordedAudioPause}
                        onEnded={handleRecordedAudioEnded}
                      />
                      <AudioPlayerControlBar className="h-11 border border-gray-200/10 bg-black px-0 py-0">
                        <AudioPlayerPlayButton className="h-11 w-14 border-0 bg-transparent text-gray-100 [--media-button-icon-height:1.15rem] [--media-button-icon-width:1.15rem]" />
                        <div aria-hidden="true" className="h-11 w-px shrink-0 bg-gray-200/20" />
                        <AudioPlayerTimeDisplay className="h-11 min-w-14 border-0 bg-transparent px-3 py-0 text-center text-[10px] leading-none text-gray-300" />
                        <div aria-hidden="true" className="h-11 w-px shrink-0 bg-gray-200/20" />
                        <AudioPlayerTimeRange className="mx-0 h-11 min-w-0 flex-1 border-0 bg-transparent px-4" />
                        <div aria-hidden="true" className="h-11 w-px shrink-0 bg-gray-200/20" />
                        <AudioPlayerDurationDisplay className="h-11 min-w-14 border-0 bg-transparent px-3 py-0 text-center text-[10px] leading-none text-gray-300" />
                        <div
                          aria-hidden="true"
                          className="hidden h-11 w-px shrink-0 bg-gray-200/20 sm:block"
                        />
                        <AudioPlayerVolumeRange className="hidden h-11 w-28 border-0 bg-transparent px-4 sm:block" />
                      </AudioPlayerControlBar>
                    </AudioPlayer>
                  </div>
                </motion.div>
              ) : null}
              {audioIssues.length > 0 ? (
                <motion.div
                  className="mt-4 max-w-sm text-center text-sm font-semibold leading-6 text-red-400"
                  role="alert"
                  aria-live="polite"
                  initial="hidden"
                  animate="visible"
                  variants={topItemVariants}
                >
                  {audioIssues[0]}
                </motion.div>
              ) : null}
            </motion.div>
          </div>

          {assessmentResult ? (
            <div className="w-full -mt-1 sm:-mt-1">
              <motion.section
                className="-mt-px w-full border border-gray-200/20 bg-[#000000] px-5 py-10 pb-14 text-center sm:px-12 sm:py-12"
                aria-labelledby="assessment-results-heading"
                initial="hidden"
                whileInView="visible"
                viewport={resultViewport}
                variants={resultSectionVariants}
              >
                <motion.header
                  className="border-b border-gray-200/15 pb-8 sm:pb-10"
                  initial="hidden"
                  whileInView="visible"
                  viewport={resultViewport}
                  variants={resultSectionVariants}
                >
                  <h3
                    id="assessment-results-heading"
                    className="mb-5 text-lg font-extrabold text-gray-200 sm:text-xl"
                    aria-label="Here Is Your Pronunciation Assessment"
                  >
                    Here Is Your Pronunciation Assessment
                  </h3>
                  <div className="mt-10 flex flex-col items-center">
                    <p className="font-bold tabular-nums text-[5.5rem] leading-[0.9] tracking-tight text-white sm:text-[5.5rem]">
                      <CountUp
                        key={assessmentResult.overall_score}
                        from={0}
                        to={getOverallScorePercent(assessmentResult.overall_score)}
                        separator=","
                        direction="up"
                        duration={1}
                        delay={0}
                        className="count-up-text"
                      />
                      %
                    </p>
                    <p className="mt-8 text-lg font-medium tracking-wide text-gray-400">
                      {assessmentResult.performance_band}
                    </p>
                  </div>
                  <p className="mx-auto mt-8 max-w-xl text-md font-light leading-7 text-gray-400">
                    {enrichedResult?.summary ?? 'Realtime pronunciation assessment completed.'}
                  </p>
                </motion.header>

                <motion.div
                  className="mt-5 w-full border-b border-gray-200/15 pb-10"
                  initial="hidden"
                  whileInView="visible"
                  viewport={resultViewport}
                  variants={resultSectionVariants}
                >
                  <h2 className="text-md font-bold capitalize text-gray-200">Phonetic Variance</h2>
                  {assessmentResult.weak_phonemes.length > 0 ? (
                    <>
                      <motion.ul
                        className="mt-6 w-full divide-y divide-gray-200/20 border border-gray-200/20"
                        variants={resultListVariants}
                      >
                        {assessmentResult.weak_phonemes
                          .slice(0, MAX_WEAK_PHONEMES_DISPLAYED)
                          .map((phoneme, index) => {
                            const tier = getWeakPhonemeTier(index)
                            return (
                              <motion.li
                                key={`${phoneme}-${index}`}
                                className={`flex items-center justify-between gap-4 border-l-[3px] bg-white/[0.02] px-4 py-3 text-gray-100 sm:px-5 sm:py-4 ${tier.rowClassName}`}
                                variants={resultItemVariants}
                              >
                                <div className="flex min-w-0 items-baseline gap-4">
                                  <span
                                    className={`shrink-0 text-[12px] font-medium capitalize tracking-[0.15em] ${tier.labelClassName}`}
                                  >
                                    {tier.label}
                                  </span>
                                  <span className="truncate font-mono text-lg font-medium tracking-tight text-gray-100">
                                    /{phoneme}/
                                  </span>
                                </div>
                                <span
                                  className={`shrink-0 text-[10px] font-medium uppercase tracking-[0.18em] ${tier.statusClassName}`}
                                >
                                  Weak
                                </span>
                              </motion.li>
                            )
                          })}
                      </motion.ul>
                      {assessmentResult.weak_phonemes.length > MAX_WEAK_PHONEMES_DISPLAYED ? (
                        <motion.p
                          className="mt-10 text-center text-xs capitalize text-gray-200"
                          variants={resultItemVariants}
                        >
                          {assessmentResult.weak_phonemes.length - MAX_WEAK_PHONEMES_DISPLAYED} more
                          weak sounds not shown
                        </motion.p>
                      ) : null}
                    </>
                  ) : (
                    <motion.p
                      className="mt-6 w-full border border-gray-200/20 px-4 py-4 text-sm capitalize text-gray-200"
                      variants={resultItemVariants}
                    >
                      No material phonetic deficits registered in this capture.
                    </motion.p>
                  )}
                </motion.div>

                <motion.div
                  className="mt-10 w-full border-b border-gray-200/15 pb-10 text-center"
                  initial="hidden"
                  whileInView="visible"
                  viewport={resultViewport}
                  variants={resultSectionVariants}
                >
                  <h2 className="text-md font-bold capitalize text-gray-200">Session metrics</h2>
                  <motion.ul
                    className="mt-6 w-full divide-y divide-gray-200/20 border border-gray-200/20"
                    variants={resultListVariants}
                  >
                    {[
                      {
                        label: 'Accuracy',
                        display: `${formatMetricNumber(enrichedResult?.metrics.accuracy_percent, 1)}%`,
                      },
                      {
                        label: 'Pace (In Words Per Minute)',
                        display: `${formatMetricNumber(enrichedResult?.metrics.speech_pace_wpm, 1)}`,
                      },
                      {
                        label: 'Word confidence',
                        display: formatScore(enrichedResult?.metrics.average_word_confidence),
                      },
                      {
                        label: 'Duration',
                        display: `${formatMetricNumber(enrichedResult?.metrics.duration_seconds, 1)}s`,
                      },
                    ].map((metric) => (
                      <motion.li
                        key={metric.label}
                        className="flex items-center justify-between gap-6 bg-white/[0.02] px-4 py-3.5 sm:px-5 sm:py-4"
                        variants={resultItemVariants}
                      >
                        <span className="shrink-0 text-sm font-medium capitalize text-gray-200">
                          {metric.label}
                        </span>
                        <span className="truncate font-mono text-lg font-semibold tabular-nums text-gray-100">
                          {metric.display}
                        </span>
                      </motion.li>
                    ))}
                  </motion.ul>
                </motion.div>

                <motion.section
                  className="mt-10 w-full border-b border-gray-200/15 pb-10 text-center"
                  initial="hidden"
                  whileInView="visible"
                  viewport={resultViewport}
                  variants={resultSectionVariants}
                >
                  <h2 className="text-md font-bold capitalize text-gray-200">
                    Prescribed interventions
                  </h2>
                  {enrichedResult?.actionChecklist?.length ? (
                    <motion.ul
                      className="mt-6 w-full divide-y divide-gray-200/20 border border-gray-200/20"
                      variants={resultListVariants}
                    >
                      {enrichedResult.actionChecklist.map((item, index) => (
                        <motion.li
                          key={`${item}-${index}`}
                          className="flex items-stretch bg-white/[0.02]"
                          variants={resultItemVariants}
                        >
                          <div className="flex w-14 shrink-0 items-center justify-center border-r border-gray-200/20 py-4 sm:w-16 sm:py-5">
                            <span className="font-mono text-xl font-semibold tabular-nums leading-none text-gray-200 sm:text-xl">
                              {String(index + 1).padStart(2, '0')}
                            </span>
                          </div>
                          <div className="flex flex-1 items-center px-4 py-3.5 sm:px-5 sm:py-4">
                            <span className="text-sm leading-7 text-gray-300">{item}</span>
                          </div>
                        </motion.li>
                      ))}
                    </motion.ul>
                  ) : (
                    <motion.p
                      className="mt-6 w-full border border-gray-200/20 bg-white/[0.02] px-4 py-4 text-sm text-gray-400"
                      variants={resultItemVariants}
                    >
                      Submit another capture to generate an intervention sequence.
                    </motion.p>
                  )}
                </motion.section>

                {enrichedResult?.wordDiagnostics.weakest_words?.length ||
                enrichedResult?.wordDiagnostics.strongest_words?.length ? (
                  <motion.div
                    className="mt-10 grid w-full gap-10 lg:grid-cols-2"
                    initial="hidden"
                    whileInView="visible"
                    viewport={resultViewport}
                    variants={resultSectionVariants}
                  >
                    <motion.div variants={resultItemVariants}>
                      <h2 className="text-md font-bold capitalize text-gray-200">
                        Lexical deficits
                      </h2>
                      <motion.ul
                        className="mt-6 w-full divide-y divide-gray-200/20 border border-gray-200/20"
                        variants={resultListVariants}
                      >
                        {(enrichedResult?.wordDiagnostics.weakest_words ?? []).map(
                          (item, index) => (
                            <motion.li
                              key={`${item.word}-${index}`}
                              className="flex items-center justify-between gap-4 bg-white/[0.02] px-4 py-3.5 sm:px-5 sm:py-4"
                              variants={resultItemVariants}
                            >
                              <span className="truncate text-sm font-medium capitalize text-gray-300">
                                {item.word}
                              </span>
                              <span className="shrink-0 font-mono text-lg font-semibold tabular-nums text-gray-100">
                                {formatScore(item.score)}
                              </span>
                            </motion.li>
                          ),
                        )}
                      </motion.ul>
                    </motion.div>

                    <motion.div variants={resultItemVariants}>
                      <h2 className="text-md font-bold capitalize text-gray-200">
                        Lexical strengths
                      </h2>
                      <motion.ul
                        className="mt-6 w-full divide-y divide-gray-200/20 border border-gray-200/20"
                        variants={resultListVariants}
                      >
                        {(enrichedResult?.wordDiagnostics.strongest_words ?? []).map(
                          (item, index) => (
                            <motion.li
                              key={`${item.word}-${index}`}
                              className="flex items-center justify-between gap-4 bg-white/[0.02] px-4 py-3.5 sm:px-5 sm:py-4"
                              variants={resultItemVariants}
                            >
                              <span className="truncate text-sm font-medium capitalize text-gray-300">
                                {item.word}
                              </span>
                              <span className="shrink-0 font-mono text-lg font-semibold tabular-nums text-gray-100">
                                {formatScore(item.score)}
                              </span>
                            </motion.li>
                          ),
                        )}
                      </motion.ul>
                    </motion.div>
                  </motion.div>
                ) : null}

                {assessmentResult.word_scores.length > 0 ? (
                  <motion.section
                    className="mt-6 w-full border-t border-gray-200/20 pt-6 text-left"
                    initial="hidden"
                    whileInView="visible"
                    viewport={resultViewport}
                    variants={resultSectionVariants}
                  >
                    <div className="flex items-center justify-between gap-4">
                      <h2 className="text-md font-bold capitalize text-gray-200">Word scores</h2>
                      <button
                        type="button"
                        onClick={() => setShowAdvancedDetails((previous) => !previous)}
                        className="shrink-0 text-sm font-medium capitalize text-gray-500 hover:text-gray-300"
                      >
                        {showAdvancedDetails ? 'Hide' : 'Show all'}
                      </button>
                    </div>

                    {showAdvancedDetails ? (
                      <motion.ul
                        className="mt-6 w-full divide-y divide-gray-200/20 border border-gray-200/20"
                        initial="hidden"
                        animate="visible"
                        variants={resultListVariants}
                      >
                        {[...assessmentResult.word_scores]
                          .sort((a, b) => getWordScoreValue(a) - getWordScoreValue(b))
                          .map((wordScore, index) => (
                            <motion.li
                              key={`${getWordScoreLabel(wordScore)}-${index}`}
                              className="flex items-center justify-between gap-6 bg-white/[0.02] px-4 py-3.5 sm:px-5 sm:py-4"
                              variants={resultItemVariants}
                            >
                              <span className="truncate text-sm font-medium capitalize text-gray-300">
                                {getWordScoreLabel(wordScore)}
                              </span>
                              <span className="shrink-0 font-mono text-lg font-semibold tabular-nums text-gray-100">
                                {formatScore(getWordScoreValue(wordScore))}
                              </span>
                            </motion.li>
                          ))}
                      </motion.ul>
                    ) : null}
                  </motion.section>
                ) : null}
              </motion.section>
            </div>
          ) : null}
        </div>
      </section>
    </main>
  )
}
