'use client'

import { useEffect, useState } from 'react'

import SiteLoader from '@/components/site-loader'

const INTRO_DURATION_MS = 2000

type IntroLoaderProps = {
  children: React.ReactNode
}

export default function IntroLoader({ children }: IntroLoaderProps) {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setIsLoading(false)
    }, INTRO_DURATION_MS)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [])

  if (isLoading) {
    return <SiteLoader />
  }

  return children
}
