/**
 * Simple client-side logger utility
 * In development: logs to console
 * In production: sends errors to Sentry, logs warnings as breadcrumbs
 */

import * as Sentry from '@sentry/nextjs'

const isDevelopment = process.env.NODE_ENV === 'development'

function sanitize(message: string): string {
  return message.replace(/[\n\r\f\t\v]/g, '_')
}

export const logger = {
  error: (message: string, error?: unknown) => {
    const safe = sanitize(message)
    if (isDevelopment) {
      console.error(safe, error)
    } else if (error) {
      Sentry.captureException(error, { level: 'error' })
    } else {
      Sentry.captureMessage(safe, { level: 'error' })
    }
  },

  warn: (message: string, error?: unknown) => {
    const safe = sanitize(message)
    if (isDevelopment) {
      console.warn(safe, error)
    } else {
      Sentry.addBreadcrumb({ message: safe, level: 'warning' })
    }
  },

  info: (message: string, data?: unknown) => {
    if (isDevelopment) {
      console.info(sanitize(message), data)
    }
  },

  debug: (message: string, data?: unknown) => {
    if (isDevelopment) {
      console.debug(sanitize(message), data)
    }
  },
}
