import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactCompiler: true,
  turbopack: {
    resolveAlias: {},
    rules: {},
  },
}

export default nextConfig
