<script setup lang="ts">
import { computed } from 'vue'
import { CalendarDays, Trophy, UsersRound } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { RepeatTeammate, RepeatTeammatesResult } from '@/lib/api'

const props = defineProps<{
  data: RepeatTeammatesResult
  disabled?: boolean
}>()

const emit = defineEmits<{
  openMatchup: [teammate: RepeatTeammate]
}>()

const teammates = computed(() => (
  [...props.data.teammates].sort((a, b) => {
    if (b.games_together !== a.games_together) return b.games_together - a.games_together
    return b.last_played - a.last_played
  })
))

function formatPlayer(player: RepeatTeammate) {
  return player.tag ? `${player.name}#${player.tag}` : player.name
}

function formatDate(timestamp: number) {
  if (!timestamp) return 'Unknown'
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(timestamp))
}

function winRate(player: RepeatTeammate) {
  if (!player.games_together) return 0
  return Math.round((player.wins_together / player.games_together) * 100)
}
</script>

<template>
  <Card class="w-full border-primary/20 bg-card/90 shadow-[0_24px_80px_-55px_rgba(0,0,0,1)] backdrop-blur">
    <CardHeader class="border-b border-primary/15 bg-background/55">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div class="space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <Badge class="border border-accent/25 bg-accent/12 text-accent">Recurring Allies</Badge>
            <Badge variant="outline">{{ data.total_matches_scanned }} scanned matches</Badge>
          </div>

          <div>
            <CardTitle class="font-display text-2xl sm:text-3xl">
              {{ data.player.name }}#{{ data.player.tag }}
            </CardTitle>
            <p class="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              Allies who ended up under the same banner at least twice across the scanned match history.
            </p>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 lg:min-w-[320px]">
          <div class="rounded-2xl border border-primary/15 bg-background/75 p-4">
            <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Matches Scanned</div>
            <div class="mt-2 text-2xl font-semibold">{{ data.total_matches_scanned }}</div>
          </div>
          <div class="rounded-2xl border border-primary/15 bg-background/75 p-4">
            <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Recurring Allies</div>
            <div class="mt-2 text-2xl font-semibold">{{ data.total_repeat_teammates }}</div>
          </div>
        </div>
      </div>
    </CardHeader>

    <CardContent class="space-y-4 pt-6">
      <div
        v-if="teammates.length === 0"
        class="rounded-[1.5rem] border border-dashed border-primary/20 bg-background/75 p-8 text-center text-sm text-muted-foreground"
      >
        No recurring allies were found for this account in the scanned matches.
      </div>

      <div v-else class="grid gap-4 lg:grid-cols-2">
        <button
          v-for="teammate in teammates"
          :key="teammate.puuid"
          type="button"
          class="rounded-[1.5rem] border border-primary/15 bg-background/75 p-5 text-left transition hover:-translate-y-0.5 hover:border-primary/35 hover:bg-background disabled:cursor-not-allowed disabled:opacity-70"
          :disabled="disabled"
          @click="emit('openMatchup', teammate)"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-lg font-semibold">{{ formatPlayer(teammate) }}</div>
              <div class="mt-1 text-sm text-muted-foreground">Queued together across multiple matches. Click to open the shared match dossier.</div>
            </div>
            <Badge variant="secondary">{{ teammate.games_together }} games together</Badge>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-3">
            <div class="rounded-2xl border border-primary/15 bg-muted/50 p-3">
              <div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                <UsersRound class="size-4 text-primary" />
                Together
              </div>
              <div class="mt-2 text-xl font-semibold">{{ teammate.games_together }}</div>
            </div>

            <div class="rounded-2xl border border-primary/15 bg-muted/50 p-3">
              <div class="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Met Total</div>
              <div class="mt-2 text-xl font-semibold">{{ teammate.games_met }}</div>
            </div>

            <div class="rounded-2xl border border-primary/15 bg-muted/50 p-3">
              <div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                <Trophy class="size-4 text-primary" />
                Wins
              </div>
              <div class="mt-2 text-xl font-semibold">{{ teammate.wins_together }} <span class="text-sm text-muted-foreground">({{ winRate(teammate) }}%)</span></div>
            </div>

            <div class="rounded-2xl border border-primary/15 bg-muted/50 p-3">
              <div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                <CalendarDays class="size-4 text-primary" />
                Last Played
              </div>
              <div class="mt-2 text-sm font-medium">{{ formatDate(teammate.last_played) }}</div>
            </div>
          </div>

          <div class="mt-4 flex flex-wrap gap-2">
            <Badge
              v-for="mode in teammate.game_modes"
              :key="`${teammate.puuid}-${mode}`"
              variant="outline"
            >
              {{ mode }}
            </Badge>
          </div>
        </button>
      </div>
    </CardContent>
  </Card>
</template>
