import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'

const ACCESS_TOKEN_COOKIE_NAME = 'access_token'

export function proxy(request: NextRequest) {
  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)?.value
  const isLoginMfaVerification =
    request.nextUrl.pathname === '/mfa/verify' &&
    request.nextUrl.searchParams.get('mode') === 'login'

  if (isLoginMfaVerification) {
    return NextResponse.next()
  }

  if (!accessToken) {
    return NextResponse.redirect(new URL('/register', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/mfa', '/mfa/verify'],
}
