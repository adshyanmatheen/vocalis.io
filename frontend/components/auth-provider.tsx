'use client'

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { getSessionUserWithRefresh, type AuthUser } from '@/lib/api'

type AuthContextValue = {
  user: AuthUser | null
  loading: boolean
  refreshAuth: () => Promise<AuthUser | null>
}

const AuthContext = createContext<AuthContextValue | null>(null)

const PUBLIC_PATH_PREFIXES = ['/', '/sign-in', '/register', '/mfa']

const isPublicPath = (pathname: string) => {
  if (pathname === '/') {
    return true
  }
  return PUBLIC_PATH_PREFIXES.some((prefix) =>
    prefix === '/' ? pathname === '/' : pathname.startsWith(prefix),
  )
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshAuth = useCallback(async () => {
    const nextUser = await getSessionUserWithRefresh()
    setUser(nextUser)
    return nextUser
  }, [])

  useEffect(() => {
    let cancelled = false
    const bootstrapAuth = async () => {
      setLoading(true)
      try {
        const nextUser = await getSessionUserWithRefresh()
        if (cancelled) {
          return
        }
        setUser(nextUser)
        if (!nextUser && !isPublicPath(pathname)) {
          router.replace('/sign-in')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void bootstrapAuth()
    return () => {
      cancelled = true
    }
  }, [pathname, router])

  const value = useMemo(
    () => ({
      user,
      loading,
      refreshAuth,
    }),
    [loading, refreshAuth, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider.')
  }
  return context
}
