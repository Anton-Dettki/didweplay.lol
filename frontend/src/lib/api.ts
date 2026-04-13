import { ref, type Ref } from 'vue'

const API_BASE_URL = 'http://localhost:8000'

export interface PlayerInfo {
  name: string
  tag: string
  puuid?: string | null
}

export interface MatchPlayer {
  champion: string
  kills: number
  deaths: number
  assists: number
  win: boolean
  position: string
  damage: number
  cs: number
  vision_score: number
  gold_earned: number
  level: number
}

export interface MatchDetail {
  match_id: string
  game_mode: string
  game_type: string
  game_version: string
  platform_id: string
  queue_id: number
  map_id: number
  timestamp: number
  duration: number
  player1: MatchPlayer
  player2: MatchPlayer
  same_team: boolean
}

export interface MatchupResult {
  player1: PlayerInfo
  player2: PlayerInfo
  total_common: number
  stats: {
    same_team: number
    opponents: number
    player1_wins: number
    player2_wins: number
  }
  matches: MatchDetail[]
  filters?: {
    game_modes: string[]
  }
}

export interface RepeatTeammate {
  puuid: string
  name: string
  tag: string
  games_met: number
  games_together: number
  opponent_games: number
  wins_together: number
  last_played: number
  game_modes: string[]
}

export interface RepeatTeammatesResult {
  player: PlayerInfo
  total_matches_scanned: number
  total_repeat_teammates: number
  teammates: RepeatTeammate[]
}

export interface MatchupPairRequest {
  player1Name: string
  player1Tag: string
  player1Puuid: string
  player2Name: string
  player2Tag: string
  player2Puuid: string
  region: string
}

interface StreamState<T> {
  loading: Ref<boolean>
  progress: Ref<string>
  result: Ref<T | null>
  error: Ref<string>
  run: (endpoint: string, params: Record<string, string>) => Promise<void>
}

function createStreamingRequest<T>(): StreamState<T> {
  const loading = ref(false)
  const progress = ref('')
  const result = ref<T | null>(null) as Ref<T | null>
  const error = ref('')

  async function run(endpoint: string, params: Record<string, string>) {
    loading.value = true
    progress.value = ''
    result.value = null
    error.value = ''

    try {
      const query = new URLSearchParams(params)
      const response = await fetch(`${API_BASE_URL}${endpoint}?${query}`)

      if (!response.ok) {
        error.value = `Server error: ${response.status}`
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        error.value = 'No response stream'
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const dataLine = line.trim()
          if (!dataLine.startsWith('data: ')) continue

          const event = JSON.parse(dataLine.slice(6)) as
            | { type: 'progress'; message: string }
            | { type: 'result'; data: T }
            | { type: 'error'; message: string }

          if (event.type === 'progress') {
            progress.value = event.message
          } else if (event.type === 'result') {
            result.value = event.data
          } else if (event.type === 'error') {
            error.value = event.message
          }
        }
      }
    } catch (e: any) {
      error.value = e.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { loading, progress, result, error, run }
}

export function useMatchupCheck() {
  const request = createStreamingRequest<MatchupResult>()

  return {
    loading: request.loading,
    progress: request.progress,
    result: request.result,
    error: request.error,
    check: (player1: string, player2: string, region: string) => request.run('/api/check', { player1, player2, region }),
    checkPair: (pair: MatchupPairRequest) => request.run('/api/check-pair', {
      player1_name: pair.player1Name,
      player1_tag: pair.player1Tag,
      player1_puuid: pair.player1Puuid,
      player2_name: pair.player2Name,
      player2_tag: pair.player2Tag,
      player2_puuid: pair.player2Puuid,
      region: pair.region,
    }),
  }
}

export function useRepeatTeammatesCheck() {
  const request = createStreamingRequest<RepeatTeammatesResult>()

  return {
    loading: request.loading,
    progress: request.progress,
    result: request.result,
    error: request.error,
    check: (player: string, region: string) => request.run('/api/repeat-teammates', { player, region }),
  }
}
