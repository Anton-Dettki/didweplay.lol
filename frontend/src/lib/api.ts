import { ref } from 'vue'

export interface PlayerInfo {
  name: string
  tag: string
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

export function useMatchupCheck() {
  const loading = ref(false)
  const progress = ref('')
  const result = ref<MatchupResult | null>(null)
  const error = ref('')

  async function check(player1: string, player2: string, region: string) {
    loading.value = true
    progress.value = ''
    result.value = null
    error.value = ''

    try {
      const params = new URLSearchParams({ player1, player2, region })
      const response = await fetch(`http://localhost:8000/api/check?${params}`)

      if (!response.ok) {
        error.value = `Server error: ${response.status}`
        loading.value = false
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        error.value = 'No response stream'
        loading.value = false
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
          const json = JSON.parse(dataLine.slice(6))

          if (json.type === 'progress') {
            progress.value = json.message
          } else if (json.type === 'result') {
            result.value = json.data
          } else if (json.type === 'error') {
            error.value = json.message
          }
        }
      }
    } catch (e: any) {
      error.value = e.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { loading, progress, result, error, check }
}
