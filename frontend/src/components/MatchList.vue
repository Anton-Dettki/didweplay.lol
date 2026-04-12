<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import MatchCard from './MatchCard.vue'
import type { MatchupResult } from '@/lib/api'

const props = defineProps<{ data: MatchupResult }>()

const modeFilter = ref('all')
const relationFilter = ref('all')

const gameModes = computed(() => props.data.filters?.game_modes || [])

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
    <div class="flex items-center gap-3 flex-wrap">
      <Select v-model="modeFilter">
        <SelectTrigger class="w-[160px]">
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
        <SelectTrigger class="w-[160px]">
          <SelectValue placeholder="Relationship" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All</SelectItem>
          <SelectItem value="same_team">Same Team</SelectItem>
          <SelectItem value="opponents">Opponents</SelectItem>
        </SelectContent>
      </Select>

      <span class="text-sm text-muted-foreground ml-auto">
        {{ filtered.length }} match{{ filtered.length !== 1 ? 'es' : '' }}
      </span>
    </div>

    <MatchCard
      v-for="match in filtered"
      :key="match.match_id"
      :match="match"
      :player1="data.player1"
      :player2="data.player2"
    />

    <div v-if="filtered.length === 0" class="text-center text-muted-foreground py-8">
      No matches found with these filters.
    </div>
  </div>
</template>
