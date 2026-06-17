/**
 * Simple client-side logger utility
 * In development: logs to console
 * In production: sends errors to Sentry, logs warnings as breadcrumbs
 */

import * as Sentry from '@sentry/nextjs'

const isDevelopment = process.env.NODE_ENV === 'development'

export const logger = {
  error: (message: string, error?: unknown) => {
    const safe = message.replace(/[\n\r\f\t\v]/g, '_')
    if (isDevelopment) {
      console.error(safe)
      if (error) console.error(error)
    } else if (error) {
      Sentry.captureException(error, { level: 'error' })
    } else {
      Sentry.captureMessage(safe, { level: 'error' })
    }
  },

  warn: (message: string, error?: unknown) => {
    const safe = message.replace(/[\n\r\f\t\v]/g, '_')
    if (isDevelopment) {
      console.warn(safe)
      if (error) console.warn(error)
    } else {
      Sentry.addBreadcrumb({ message: safe, level: 'warning' })
    }
  },

  info: (message: string, data?: unknown) => {
    if (isDevelopment) {
      console.info(message.replace(/[\n\r\f\t\v]/g, '_'), data)
    }
  },

  debug: (message: string, data?: unknown) => {
    if (isDevelopment) {
      console.debug(message.replace(/[\n\r\f\t\v]/g, '_'), data)
    }
  },
}
