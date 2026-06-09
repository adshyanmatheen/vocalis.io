'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-black text-white">
      <div className="space-y-4 text-center">
        <h1 className="text-4xl font-bold">Something went wrong</h1>
        <p className="text-lg text-gray-400">An unexpected error occurred.</p>
        <p className="text-sm text-gray-500">{error.message}</p>
        <button
          onClick={() => reset()}
          className="mt-6 inline-flex items-center justify-center rounded-md bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-200"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
