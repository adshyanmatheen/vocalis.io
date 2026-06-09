'use client'

import { Button } from '@/components/ui/button'
import { FieldGroup, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { csrfHeader, getApiBaseUrl } from '@/lib/api'
import { PageBackground, DotMetersRow } from '@/lib/page-layouts'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function SignIn() {
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)

    const trimmedUsername = username.trim()
    if (!trimmedUsername) {
      setError('Please Enter Your Username.')
      return
    }

    if (!password) {
      setError('Please Enter Your Password.')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...csrfHeader() },
        credentials: 'include',
        body: JSON.stringify({
          username: trimmedUsername,
          password,
        }),
      })

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload?.detail || payload?.message || 'Sign-in failed.')
      }

      if (payload?.mfa_required) {
        sessionStorage.setItem('vocalis_mfa_temporary_token', payload?.temporary_token ?? '')
        router.push('/mfa/verify?mode=login')
        return
      }

      router.push('/home')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'The Sign-in Failed.'
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
            aria-label="Welcome Back To Vocalis"
          >
            Welcome Back To Vocalis
          </h3>
          <p
            className="max-w-sm text-sm font-semibold mb-10 leading-6 text-gray-300 sm:max-w-none sm:text-base"
            aria-label="Let's Sign In Back To Your Vocalis Account"
          >
            Let&apos;s Sign In Back To Your Vocalis Account
          </p>
          <form onSubmit={handleSubmit}>
            <FieldGroup className="w-full px-5 gap-4">
              <FieldLabel
                className="text-gray-400 capitalize text-sm"
                htmlFor="input-field-username"
              >
                Enter Your Username
              </FieldLabel>
              <Input
                id="input-field-username"
                type="text"
                placeholder="swift_owl_247"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                disabled={loading}
                className="w-full border border-gray-500 bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-0 focus:outline-none focus:ring-1 focus:ring-gray-600/40 focus:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50"
              />
              <FieldLabel
                className="text-gray-400 capitalize text-sm mt-5"
                htmlFor="input-field-password"
              >
                Enter Your Password
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
                className="mt-4 px-5 text-left text-sm text-red-400"
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
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>
            </div>
          </form>
          <div className="mt-8 flex w-full items-center justify-center gap-2 sm:mt-10 sm:w-auto">
            <span className="text-sm text-gray-400 capitalize">Don&apos;t Have An Account?</span>
            <span className="text-sm text-gray-400 underline underline-offset-4 hover:underline">
              <Link href="/register">Create Account</Link>
            </span>
          </div>
        </div>
      </section>
    </main>
  )
}
