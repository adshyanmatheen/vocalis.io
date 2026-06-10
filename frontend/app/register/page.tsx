'use client'

import { Button } from '@/components/ui/button'
import { FieldGroup, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { PageBackground, DotMetersRow } from '@/lib/page-layouts'
import { playSound } from '@/lib/sound-engine'
import { switch001Sound } from '@/lib/switch-001'
import { csrfHeader, getApiBaseUrl } from '@/lib/api'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

const NAME_PATTERN = /^[A-Za-z\s]{2,32}$/

export default function Register() {
  const handlePlay = () => {
    void playSound(switch001Sound.dataUri)
  }

  const router = useRouter()
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const validateInputs = () => {
    const trimmedName = name.trim()

    if (!NAME_PATTERN.test(trimmedName)) {
      return 'Your Name Must Be 2-32 Characters And Contain Only Letters And Spaces.'
    }

    if (password.length < 8) {
      return 'The Password Must Be At Least 8 Characters Long.'
    }

    if (!/[A-Z]/.test(password)) {
      return 'The Password Must Include At Least One Uppercase Letter.'
    }

    if (!/[a-z]/.test(password)) {
      return 'The Password Must Include At Least One Lowercase Letter.'
    }

    if (!/\d/.test(password)) {
      return 'The Password Must Include At Least One Number.'
    }

    return null
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)

    const validationError = validateInputs()
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...csrfHeader() },
        credentials: 'include',
        body: JSON.stringify({
          name: name.trim(),
          password,
        }),
      })

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload?.detail || payload?.message || 'Registration failed.')
      }

      router.push('/mfa')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'The Registration Failed.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

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
            Let&apos;s Create Your Personal Vocalis Account
          </p>
          <form onSubmit={handleSubmit}>
            <FieldGroup className="w-full px-5 gap-4">
              <FieldLabel className="text-gray-400 capitalize text-sm" htmlFor="input-field-name">
                Enter Your Preferred Full Name
              </FieldLabel>
              <Input
                id="input-field-name"
                type="text"
                placeholder="Matilda Smith"
                value={name}
                onChange={(event) => setName(event.target.value)}
                disabled={loading}
                className="w-full border border-gray-500 bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-0 focus:outline-none focus:ring-1 focus:ring-gray-600/40 focus:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50"
              />
              <FieldLabel
                className="text-gray-400 capitalize text-sm mt-5"
                htmlFor="input-field-password"
              >
                Enter Your Preferred Password
              </FieldLabel>
              <Input
                id="input-field-password"
                type="password"
                placeholder="*********"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={loading}
                className="w-full border border-gray-500 bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-0 focus:outline-none focus:ring-1 focus:ring-gray-600/40 focus:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </FieldGroup>

            {error ? (
              <div
                className="mt-4 px-5 text-center text-sm text-red-400"
                role="alert"
                aria-live="polite"
              >
                {error}
              </div>
            ) : null}

            <DotMetersRow />
            <div className="mt-8 flex w-full items-center justify-center gap-2 sm:mt-10 sm:w-auto">
              <Button
                size="lg"
                type="submit"
                className="w-full max-w-52 font-bold capitalize text-md sm:w-auto"
                disabled={loading}
                onClick={handlePlay}
              >
                {loading ? 'Creating...' : 'Create Account'}
              </Button>
            </div>
          </form>
          <div className="mt-8 flex w-full items-center justify-center gap-2 sm:mt-10 sm:w-auto">
            <span className="text-sm text-gray-400 capitalize">Already have an account?</span>
            <span className="text-sm text-gray-400 underline underline-offset-4 hover:underline">
              <Link href="/sign-in">Sign In</Link>
            </span>
          </div>
        </div>
      </section>
    </main>
  )
}
