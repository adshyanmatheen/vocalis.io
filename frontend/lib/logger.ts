/**
 * Simple client-side logger utility
 * In development: logs to console
 * In production: sends errors to Sentry, logs warnings as breadcrumbs
 */

import * as Sentry from '@sentry/nextjs'

const isDevelopment = process.env.NODE_ENV === 'development'

export const logger = {
  error: (message: string, error?: unknown) => {
    const safe = message.replace(/\n|\r/g, '')
    if (isDevelopment) {
      console.error(safe)
    } else if (error) {
      Sentry.captureException(error, { level: 'error' })
    } else {
      Sentry.captureMessage(safe, { level: 'error' })
    }
  },

  warn: (message: string) => {
    const safe = message.replace(/\n|\r/g, '')
    if (isDevelopment) {
      console.warn(safe)
    } else {
      Sentry.addBreadcrumb({ message: safe, level: 'warning' })
    }
  },

  info: (message: string) => {
    if (isDevelopment) {
      console.info(message.replace(/\n|\r/g, ''))
    }
  },

  debug: (message: string) => {
    if (isDevelopment) {
      console.debug(message.replace(/\n|\r/g, ''))
    }
  },
}
