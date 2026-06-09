/**
 * Simple client-side logger utility
 * In development: logs to console
 * In production: silent (can be extended with Sentry, etc.)
 */

const isDevelopment = process.env.NODE_ENV === 'development'

export const logger = {
  error: (message: string, error?: unknown) => {
    if (isDevelopment) {
      console.error(message, error)
    }
    // TODO: Send to error tracking service (Sentry, etc.) in production
  },

  warn: (message: string, error?: unknown) => {
    if (isDevelopment) {
      console.warn(message, error)
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
