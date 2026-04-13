<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import MatchCard from './MatchCard.vue'
import type { MatchupResult } from '@/lib/api'

const props = defineProps<{
  data: MatchupResult
  initialRelationFilter?: 'all' | 'same_team' | 'opponents'
}>()

const modeFilter = ref('all')
const relationFilter = ref(props.initialRelationFilter ?? 'all')

watch(
  () => props.initialRelationFilter,
  (value) => {
    relationFilter.value = value ?? 'all'
  },
)

const gameModes = computed(() => props.data.filters?.game_modes || [])
const modeBreakdown = computed(() =>
  gameModes.value
    .map((mode) => ({
      mode,
      count: props.data.matches.filter((match) => match.game_mode === mode).length,
    }))
    .sort((left, right) => right.count - left.count),
)

const filtered = computed(() => {
  return props.data.matches.filter((m) => {
    if (modeFilter.value !== 'all' && m.game_mode !== modeFilter.value) return false
    if (relationFilter.value === 'same_team' && !m.same_team) return false
    if (relationFilter.value === 'opponents' && m.same_team) return false
    return true
  }).sort((a, b) => b.timestamp - a.timestamp)
})
</script>

<template>
  <div class="w-full space-y-4">
    <Card class="border-primary/20 bg-card/90 shadow-sm backdrop-blur">
      <CardHeader class="border-b border-primary/15 bg-background/55">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <CardTitle class="font-display text-2xl">Clash Timeline</CardTitle>
            <p class="mt-2 text-sm text-muted-foreground">
              Filter the dossier by queue type or whether they fought side by side versus across the map.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <Select v-model="modeFilter">
              <SelectTrigger class="w-[180px] rounded-xl bg-background/80">
                <SelectValue placeholder="Game Mode" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Modes</SelectItem>
                <SelectItem v-for="mode in gameModes" :key="mode" :value="mode">
                  {{ mode }}
                </SelectItem>
              </SelectContent>
            </Select>

            <Select v-model="relationFilter">
              <SelectTrigger class="w-[180px] rounded-xl bg-background/80">
                <SelectValue placeholder="Relationship" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="same_team">Same Team</SelectItem>
                <SelectItem value="opponents">Opponents</SelectItem>
              </SelectContent>
            </Select>

            <span class="text-sm text-muted-foreground">
              {{ filtered.length }} showing
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent class="pt-5">
        <div class="flex flex-wrap gap-2">
          <Badge v-for="entry in modeBreakdown" :key="entry.mode" variant="outline">
            {{ entry.mode }} · {{ entry.count }}
          </Badge>
        </div>
      </CardContent>
    </Card>

    <MatchCard
      v-for="match in filtered"
      :key="match.match_id"
      :match="match"
      :player1="data.player1"
      :player2="data.player2"
    />

    <div v-if="filtered.length === 0" class="rounded-[1.5rem] border border-primary/15 bg-card/90 py-8 text-center text-muted-foreground shadow-sm backdrop-blur">
      No matches found with these filters.
    </div>
  </div>
</template>
