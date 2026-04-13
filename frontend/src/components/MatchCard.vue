<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUpRight } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import type { MatchDetail, PlayerInfo } from '@/lib/api'
import {
  formatCompactNumber,
  formatDuration,
  formatLabel,
  formatMatchDate,
  formatPatch,
  formatPosition,
  formatRelativeTime,
  getKdaRatio,
  getLeagueOfGraphsMatchUrl,
  getOpggSummonerUrl,
} from '@/lib/matches'

const props = defineProps<{
  match: MatchDetail
  player1: PlayerInfo
  player2: PlayerInfo
}>()

const DDRAGON = 'https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion'

const date = computed(() => formatMatchDate(props.match.timestamp))
const relativeDate = computed(() => formatRelativeTime(props.match.timestamp))
const duration = computed(() => formatDuration(props.match.duration))
const patch = computed(() => formatPatch(props.match.game_version))
const matchUrl = computed(() => getLeagueOfGraphsMatchUrl(props.match))

const playerCards = computed(() => [
  {
    info: props.player1,
    stats: props.match.player1,
    profileUrl: getOpggSummonerUrl(props.player1, props.match.platform_id, props.match.match_id),
  },
  {
    info: props.player2,
    stats: props.match.player2,
    profileUrl: getOpggSummonerUrl(props.player2, props.match.platform_id, props.match.match_id),
  },
])
</script>

<template>
  <Card class="w-full border-primary/20 bg-card/90 shadow-sm backdrop-blur">
    <CardHeader class="border-b border-primary/15 bg-background/55">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div class="space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <Badge :variant="match.same_team ? 'secondary' : 'destructive'">
              {{ match.same_team ? 'Same Banner' : 'Enemy Side' }}
            </Badge>
            <Badge variant="outline">{{ match.game_mode }}</Badge>
            <Badge variant="outline">Patch {{ patch }}</Badge>
            <Badge variant="outline">{{ formatLabel(match.game_type) }}</Badge>
          </div>

          <div class="flex flex-wrap items-center gap-x-3 gap-y-2 text-sm text-muted-foreground">
            <span>{{ date }}</span>
            <span>{{ relativeDate }}</span>
            <span>{{ duration }}</span>
          </div>
        </div>

        <code class="w-fit rounded-lg bg-muted px-3 py-1 text-xs text-muted-foreground">
          {{ match.match_id }}
        </code>
      </div>
    </CardHeader>

    <CardContent class="grid gap-4 pt-5 lg:grid-cols-2">
      <div
        v-for="player in playerCards"
        :key="player.info.name + player.info.tag"
        class="rounded-[1.5rem] border border-primary/15 bg-background/75 p-4"
      >
        <div class="flex items-start gap-4">
          <img
            :src="`${DDRAGON}/${player.stats.champion}.png`"
            :alt="player.stats.champion"
            class="size-14 rounded-xl border border-primary/15 bg-muted object-cover"
            @error="($event.target as HTMLImageElement).style.display = 'none'"
          />

          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <div class="truncate text-base font-semibold">
                {{ player.info.name }}#{{ player.info.tag }}
              </div>
              <Badge :variant="player.stats.win ? 'default' : 'secondary'">
                {{ player.stats.win ? 'Win' : 'Loss' }}
              </Badge>
            </div>

            <div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <span>{{ player.stats.champion }}</span>
              <span>•</span>
              <span>{{ formatPosition(player.stats.position) }}</span>
              <span>•</span>
              <span>Lvl {{ player.stats.level }}</span>
            </div>
          </div>
        </div>

        <div class="mt-4 grid grid-cols-2 gap-3">
          <div class="rounded-xl bg-muted/70 p-3 ring-1 ring-primary/8">
            <div class="text-[11px] font-semibold uppercase tracking-[0.22em] text-primary">KDA</div>
            <div class="mt-1 text-lg font-semibold">
              {{ player.stats.kills }}/{{ player.stats.deaths }}/{{ player.stats.assists }}
            </div>
            <div class="text-xs text-muted-foreground">{{ getKdaRatio(player.stats) }} ratio</div>
          </div>

          <div class="rounded-xl bg-muted/70 p-3 ring-1 ring-primary/8">
            <div class="text-[11px] font-semibold uppercase tracking-[0.22em] text-primary">Damage</div>
            <div class="mt-1 text-lg font-semibold">{{ formatCompactNumber(player.stats.damage) }}</div>
            <div class="text-xs text-muted-foreground">champion damage</div>
          </div>

          <div class="rounded-xl bg-muted/70 p-3 ring-1 ring-primary/8">
            <div class="text-[11px] font-semibold uppercase tracking-[0.22em] text-primary">Farming</div>
            <div class="mt-1 text-lg font-semibold">{{ player.stats.cs }}</div>
            <div class="text-xs text-muted-foreground">total CS</div>
          </div>

          <div class="rounded-xl bg-muted/70 p-3 ring-1 ring-primary/8">
            <div class="text-[11px] font-semibold uppercase tracking-[0.22em] text-primary">Vision / Gold</div>
            <div class="mt-1 text-lg font-semibold">{{ player.stats.vision_score }}</div>
            <div class="text-xs text-muted-foreground">{{ formatCompactNumber(player.stats.gold_earned) }} gold</div>
          </div>
        </div>
      </div>
    </CardContent>

    <CardFooter class="flex flex-col items-start gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
      <div class="text-xs text-muted-foreground">
        External links follow the exact platform for this recorded game.
      </div>

      <div class="flex flex-wrap gap-2">
        <Button v-if="matchUrl" size="sm" as-child>
          <a :href="matchUrl" target="_blank" rel="noreferrer">
            Open Match Page
            <ArrowUpRight class="size-4" />
          </a>
        </Button>

        <template v-for="player in playerCards" :key="`${player.info.name}-${player.info.tag}-profile`">
          <Button
            v-if="player.profileUrl"
            variant="outline"
            size="sm"
            as-child
          >
            <a :href="player.profileUrl ?? undefined" target="_blank" rel="noreferrer">
              {{ player.info.name }} on OP.GG
              <ArrowUpRight class="size-4" />
            </a>
          </Button>
        </template>
      </div>
    </CardFooter>
  </Card>
</template>
