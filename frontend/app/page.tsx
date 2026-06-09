'use client'

import { Button } from '@/components/ui/button'
import { useAuth } from '@/components/auth-provider'
import { PageBackground, DotMetersRow } from '@/lib/page-layouts'
import { playSound } from '@/lib/sound-engine'
import { switch001Sound } from '@/lib/switch-001'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()
  const { refreshAuth, loading, user } = useAuth()

  const handlePlay = () => {
    void playSound(switch001Sound.dataUri)
  }

  const handleGetStarted = async () => {
    handlePlay()

    if (user) {
      router.push('/home')
      return
    }

    if (loading) {
      const nextUser = await refreshAuth()
      router.push(nextUser ? '/home' : '/register')
      return
    }

    const nextUser = await refreshAuth()
    router.push(nextUser ? '/home' : '/register')
  }

  return (
    <main className="relative min-h-svh overflow-hidden">
      <PageBackground />

      <section className="relative z-10 flex min-h-svh items-center justify-center px-4 py-8 sm:p-10">
        <div className="flex w-full max-w-xl flex-col items-center justify-center border border-gray-200/20 bg-[#000000] px-5 py-8 text-center sm:px-2.5 sm:py-10">
          <h3
            className="mb-5 text-lg font-extrabold text-gray-200 sm:text-xl"
            aria-label="Welcome To Vocalis"
          >
            Welcome To Vocalis
          </h3>
          <p
            className="max-w-sm text-sm font-semibold leading-6 text-gray-300 sm:max-w-none sm:text-base"
            aria-label="Your Adaptive Explainable AI Pronunciation Training Companion"
          >
            Your Adaptive Explainable AI Pronunciation Training Companion
          </p>
          <DotMetersRow desktopSize={53} />
          <div className="mt-8 flex w-full items-center justify-center gap-2 sm:mt-10 sm:w-auto">
            <Button
              size="lg"
              className="w-full max-w-52 font-bold capitalize text-md sm:w-auto"
              onClick={handleGetStarted}
            >
              Get Started
            </Button>
          </div>
        </div>
      </section>
    </main>
  )
}
