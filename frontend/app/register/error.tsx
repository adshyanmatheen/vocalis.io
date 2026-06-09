'use client'

import { useEffect } from 'react'

export default function RegisterError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Register page error:', error)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-black text-white">
      <div className="space-y-4 text-center">
        <h1 className="text-4xl font-bold">Registration Error</h1>
        <p className="text-lg text-gray-400">We encountered an issue during registration.</p>
        <p className="text-sm text-gray-500">{error.message}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => reset()}
            className="inline-flex items-center justify-center rounded-md bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-200"
          >
            Try again
          </button>
          <a
            href="/sign-in"
            className="inline-flex items-center justify-center rounded-md border border-gray-600 px-4 py-2 text-sm font-medium text-white hover:bg-gray-900"
          >
            Sign in
          </a>
        </div>
      </div>
    </div>
  )
}
