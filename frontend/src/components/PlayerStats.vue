<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUpRight, Clock3, Swords, UsersRound } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import type { MatchupResult } from '@/lib/api'
import {
  formatDuration,
  formatMatchDate,
  formatPatch,
  formatRelativeTime,
  getLatestMatch,
  getMostPlayedMode,
  getOpggSummonerUrl,
  getLeagueOfGraphsMatchUrl,
} from '@/lib/matches'

const props = defineProps<{ data: MatchupResult }>()

const p1WinRate = computed(() => {
  if (!props.data.total_common) return 0
  return Math.round((props.data.stats.player1_wins / props.data.total_common) * 100)
})

const p2WinRate = computed(() => {
  if (!props.data.total_common) return 0
  return Math.round((props.data.stats.player2_wins / props.data.total_common) * 100)
})

const latestMatch = computed(() => getLatestMatch(props.data))
const mostPlayedMode = computed(() => getMostPlayedMode(props.data))

const latestMatchUrl = computed(() => {
  if (!latestMatch.value) return null
  return getLeagueOfGraphsMatchUrl(latestMatch.value)
})

const player1ProfileUrl = computed(() => {
  if (!latestMatch.value) return null
  return getOpggSummonerUrl(props.data.player1, latestMatch.value.platform_id, latestMatch.value.match_id)
})

const player2ProfileUrl = computed(() => {
  if (!latestMatch.value) return null
  return getOpggSummonerUrl(props.data.player2, latestMatch.value.platform_id, latestMatch.value.match_id)
})

const sameTeamRate = computed(() => {
  if (!props.data.total_common) return 0
  return Math.round((props.data.stats.same_team / props.data.total_common) * 100)
})
</script>

<template>
  <Card class="w-full border-primary/20 bg-card/90 shadow-[0_28px_90px_-58px_rgba(0,0,0,1)] backdrop-blur">
    <CardHeader class="border-b border-primary/15 bg-background/55">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div class="space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <Badge class="border border-primary/25 bg-primary/12 text-primary">Match Found</Badge>
            <Badge variant="outline">{{ data.total_common }} shared games</Badge>
            <Badge variant="secondary">{{ sameTeamRate }}% same side</Badge>
          </div>

          <div>
            <CardTitle class="font-display text-2xl sm:text-3xl">
              {{ data.player1.name }}#{{ data.player1.tag }} vs {{ data.player2.name }}#{{ data.player2.tag }}
            </CardTitle>
            <p class="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              Rift dossier ready. Open the latest clash, compare the stat lines, and jump straight into public match history.
              <span v-if="latestMatch">
                Last recorded encounter: {{ formatMatchDate(latestMatch.timestamp) }} ({{ formatRelativeTime(latestMatch.timestamp) }}).
              </span>
            </p>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 lg:min-w-[320px]">
          <div class="rounded-2xl border border-primary/15 bg-background/75 p-4">
            <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Shared Games</div>
            <div class="mt-2 text-2xl font-semibold">{{ data.total_common }}</div>
          </div>
          <div class="rounded-2xl border border-primary/15 bg-background/75 p-4">
            <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Favored Queue</div>
            <div class="mt-2 text-lg font-semibold">{{ mostPlayedMode || 'Unknown' }}</div>
          </div>
          <div class="rounded-2xl border border-primary/15 bg-background/75 p-4">
            <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Same Banner</div>
            <div class="mt-2 flex items-center gap-2 text-lg font-semibold">
              <UsersRound class="size-4 text-primary" />
              <span>{{ data.stats.same_team }}</span>
            </div>
          </div>
          <div class="rounded-2xl border border-primary/15 bg-background/75 p-4">
            <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Opposing Side</div>
            <div class="mt-2 flex items-center gap-2 text-lg font-semibold">
              <Swords class="size-4 text-primary" />
              <span>{{ data.stats.opponents }}</span>
            </div>
          </div>
        </div>
      </div>
    </CardHeader>

    <CardContent class="grid gap-4 pt-6 lg:grid-cols-[1.3fr_0.7fr]">
      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-[1.5rem] border border-primary/15 bg-background/75 p-5">
          <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Blue Side Readout</div>
          <div class="mt-3 text-lg font-semibold">{{ data.player1.name }}#{{ data.player1.tag }}</div>
          <div class="mt-4 text-3xl font-semibold">{{ p1WinRate }}%</div>
          <div class="mt-2 text-sm text-muted-foreground">
            {{ data.stats.player1_wins }}W / {{ data.total_common - data.stats.player1_wins }}L in shared games
          </div>
        </div>

        <div class="rounded-[1.5rem] border border-primary/15 bg-background/75 p-5">
          <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Red Side Readout</div>
          <div class="mt-3 text-lg font-semibold">{{ data.player2.name }}#{{ data.player2.tag }}</div>
          <div class="mt-4 text-3xl font-semibold">{{ p2WinRate }}%</div>
          <div class="mt-2 text-sm text-muted-foreground">
            {{ data.stats.player2_wins }}W / {{ data.total_common - data.stats.player2_wins }}L in shared games
          </div>
        </div>
      </div>

      <div class="rounded-[1.5rem] border border-primary/15 bg-background/75 p-5">
        <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Latest Clash</div>

        <template v-if="latestMatch">
          <div class="mt-3 text-xl font-semibold">{{ latestMatch.game_mode }}</div>
          <div class="mt-2 flex flex-wrap gap-2">
            <Badge variant="outline">Patch {{ formatPatch(latestMatch.game_version) }}</Badge>
            <Badge variant="outline">{{ latestMatch.same_team ? 'Same Team' : 'Opponents' }}</Badge>
          </div>

          <div class="mt-5 space-y-3 text-sm">
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted-foreground">Played</span>
              <span>{{ formatMatchDate(latestMatch.timestamp) }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted-foreground">Relative</span>
              <span>{{ formatRelativeTime(latestMatch.timestamp) }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted-foreground">Duration</span>
              <span class="flex items-center gap-2">
                <Clock3 class="size-4 text-primary" />
                {{ formatDuration(latestMatch.duration) }}
              </span>
            </div>
            <div class="flex items-start justify-between gap-3">
              <span class="text-muted-foreground">Match ID</span>
              <code class="rounded-lg bg-muted px-2 py-1 text-xs">{{ latestMatch.match_id }}</code>
            </div>
          </div>
        </template>
      </div>
    </CardContent>

    <CardFooter class="flex flex-wrap gap-3">
      <Button v-if="latestMatchUrl" as-child>
        <a :href="latestMatchUrl" target="_blank" rel="noreferrer">
          Open Latest Match
          <ArrowUpRight class="size-4" />
        </a>
      </Button>

      <Button v-if="player1ProfileUrl" variant="outline" size="sm" as-child>
        <a :href="player1ProfileUrl" target="_blank" rel="noreferrer">
          {{ data.player1.name }} on OP.GG
          <ArrowUpRight class="size-4" />
        </a>
      </Button>

      <Button v-if="player2ProfileUrl" variant="outline" size="sm" as-child>
        <a :href="player2ProfileUrl" target="_blank" rel="noreferrer">
          {{ data.player2.name }} on OP.GG
          <ArrowUpRight class="size-4" />
        </a>
      </Button>
    </CardFooter>
  </Card>
</template>
