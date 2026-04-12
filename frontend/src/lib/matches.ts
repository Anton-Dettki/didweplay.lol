import type { MatchDetail, MatchPlayer, MatchupResult, PlayerInfo } from './api'

const platformSlugs: Record<string, string> = {
  BR1: 'br',
  EUN1: 'eune',
  EUW1: 'euw',
  JP1: 'jp',
  KR: 'kr',
  LA1: 'lan',
  LA2: 'las',
  ME1: 'me',
  NA1: 'na',
  OC1: 'oce',
  PH2: 'ph',
  RU: 'ru',
  SG2: 'sg',
  TH2: 'th',
  TR1: 'tr',
  TW2: 'tw',
  VN2: 'vn',
}

const positionLabels: Record<string, string> = {
  TOP: 'Top',
  JUNGLE: 'Jungle',
  MIDDLE: 'Mid',
  BOTTOM: 'Bot',
  UTILITY: 'Support',
  NONE: 'Flex',
  UNKNOWN: 'Flex',
}

export function formatLabel(value: string) {
  return value
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

export function formatMatchDate(timestamp: number) {
  if (!timestamp) return 'Unknown date'

  return new Date(timestamp).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatRelativeTime(timestamp: number) {
  if (!timestamp) return 'Unknown time'

  const diff = timestamp - Date.now()
  const ranges = [
    { amount: 1000, limit: 60, unit: 'second' },
    { amount: 60_000, limit: 60, unit: 'minute' },
    { amount: 3_600_000, limit: 24, unit: 'hour' },
    { amount: 86_400_000, limit: 7, unit: 'day' },
    { amount: 604_800_000, limit: 5, unit: 'week' },
    { amount: 2_592_000_000, limit: 12, unit: 'month' },
    { amount: 31_536_000_000, limit: Number.POSITIVE_INFINITY, unit: 'year' },
  ] as const

  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' })

  for (const range of ranges) {
    const delta = diff / range.amount
    if (Math.abs(delta) < range.limit) {
      return formatter.format(Math.round(delta), range.unit)
    }
  }

  return 'Recently'
}

export function formatDuration(seconds: number) {
  if (!seconds) return 'Unknown duration'

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

export function formatPatch(version: string) {
  if (!version) return 'Unknown patch'

  const [major, minor] = version.split('.')
  if (!major || !minor) return version

  return `${major}.${minor}`
}

export function formatPosition(position: string) {
  return positionLabels[position] || formatLabel(position)
}

export function formatCompactNumber(value: number) {
  return new Intl.NumberFormat(undefined, {
    notation: 'compact',
    maximumFractionDigits: value >= 10_000 ? 1 : 0,
  }).format(value)
}

export function getLatestMatch(data: MatchupResult) {
  return data.matches
    .slice()
    .sort((left, right) => right.timestamp - left.timestamp)[0] ?? null
}

export function getMostPlayedMode(data: MatchupResult) {
  const counts = data.matches.reduce<Record<string, number>>((acc, match) => {
    acc[match.game_mode] = (acc[match.game_mode] || 0) + 1
    return acc
  }, {})

  return Object.entries(counts)
    .sort((left, right) => right[1] - left[1])[0]?.[0] ?? null
}

export function getKdaRatio(player: MatchPlayer) {
  return ((player.kills + player.assists) / Math.max(player.deaths, 1)).toFixed(1)
}

export function getPlatformSlug(platformId: string, matchId?: string) {
  const normalizedPlatform = platformId.toUpperCase()
  if (platformSlugs[normalizedPlatform]) {
    return platformSlugs[normalizedPlatform]
  }

  const fallback = matchId?.split('_', 1)[0]?.toUpperCase()
  if (!fallback) return null

  return platformSlugs[fallback] ?? null
}

export function getLeagueOfGraphsMatchUrl(match: MatchDetail) {
  const platformSlug = getPlatformSlug(match.platform_id, match.match_id)
  const gameId = match.match_id.split('_')[1]

  if (!platformSlug || !gameId) return null

  return `https://www.leagueofgraphs.com/match/${platformSlug}/${gameId}`
}

export function getOpggSummonerUrl(player: PlayerInfo, platformId: string, matchId?: string) {
  const platformSlug = getPlatformSlug(platformId, matchId)
  if (!platformSlug) return null

  return `https://op.gg/lol/summoners/${platformSlug}/${encodeURIComponent(`${player.name}-${player.tag}`)}`
}
