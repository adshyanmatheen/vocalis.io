import { describe, expect, it } from 'vitest'
import { getModelHealthMessage, type ModelHealthResponse } from '@/lib/realtime-assessment'

describe('getModelHealthMessage', () => {
  const makeHealth = (overrides?: Partial<ModelHealthResponse>): ModelHealthResponse => ({
    ready: true,
    status: 'ready',
    cache_dir: '/cache',
    device: 'cpu',
    started_at: '2024-01-01T00:00:00Z',
    preload_task_status: 'completed',
    realtime_inference_timeout_seconds: 20,
    models: [],
    ...overrides,
  })

  it('returns null when models are ready', () => {
    expect(getModelHealthMessage(makeHealth())).toBeNull()
  })

  it('returns loading message when any model is loading', () => {
    const health = makeHealth({
      ready: false,
      models: [
        { name: 'alignment', model_id: 'm1', status: 'loading', error: null, updated_at: null },
      ],
    })
    expect(getModelHealthMessage(health)).toContain('Preparing')
  })

  it('returns failed message when any model has failed', () => {
    const health = makeHealth({
      ready: false,
      models: [
        {
          name: 'phoneme',
          model_id: 'm2',
          status: 'failed',
          error: 'OOM',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
    })
    expect(getModelHealthMessage(health)).toContain('contact support')
  })

  it('returns generic message when not ready but no models detail', () => {
    const health = makeHealth({
      ready: false,
      models: [
        { name: 'alignment', model_id: 'm1', status: 'not_loaded', error: null, updated_at: null },
      ],
    })
    expect(getModelHealthMessage(health)).toContain('not ready')
  })
})
