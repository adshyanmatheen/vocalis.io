/**
 * Simple client-side logger utility
 * In development: logs to console
 * In production: sends errors to Sentry, logs warnings as breadcrumbs
 */

import * as Sentry from '@sentry/nextjs'

const isDevelopment = process.env.NODE_ENV === 'development'

export const logger = {
  error: (message: string, error?: unknown) => {
    if (isDevelopment) {
      console.error(message, error)
    } else if (error) {
      Sentry.captureException(error, { level: 'error' })
    } else {
      Sentry.captureMessage(message, { level: 'error' })
    }
  },

  warn: (message: string, error?: unknown) => {
    if (isDevelopment) {
      console.warn(message, error)
    } else {
      Sentry.addBreadcrumb({ message, level: 'warning' })
    }
  },

  info: (message: string, data?: unknown) => {
    if (isDevelopment) {
      console.info(message, data)
    }
  },

  debug: (message: string, data?: unknown) => {
    if (isDevelopment) {
      console.debug(message, data)
    }
  },
}
