<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { MatchDetail, PlayerInfo } from '@/lib/api'

const props = defineProps<{
  match: MatchDetail
  player1: PlayerInfo
  player2: PlayerInfo
}>()

const DDRAGON = 'https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion'

const date = computed(() => {
  if (!props.match.timestamp) return '?'
  return new Date(props.match.timestamp).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
  })
})

const duration = computed(() => {
  const s = props.match.duration
  if (!s) return ''
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
})
</script>

<template>
  <Card class="w-full">
    <CardContent class="p-4">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <Badge :variant="match.same_team ? 'secondary' : 'destructive'">
            {{ match.same_team ? 'Same Team' : 'Opponents' }}
          </Badge>
          <Badge variant="outline">{{ match.game_mode }}</Badge>
        </div>
        <div class="text-sm text-muted-foreground">
          {{ date }}
          <span v-if="duration" class="ml-2">{{ duration }}</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <!-- Player 1 -->
        <div class="flex items-center gap-3" :class="{ 'opacity-50': !match.player1.win }">
          <img
            :src="`${DDRAGON}/${match.player1.champion}.png`"
            :alt="match.player1.champion"
            class="w-10 h-10 rounded-lg"
            @error="($event.target as HTMLImageElement).style.display = 'none'"
          />
          <div>
            <div class="font-medium text-sm">{{ player1.name }}</div>
            <div class="text-xs text-muted-foreground">{{ match.player1.champion }}</div>
            <div class="text-sm font-mono">
              {{ match.player1.kills }}/{{ match.player1.deaths }}/{{ match.player1.assists }}
            </div>
          </div>
          <Badge :variant="match.player1.win ? 'default' : 'secondary'" class="ml-auto text-xs">
            {{ match.player1.win ? 'Win' : 'Loss' }}
          </Badge>
        </div>

        <!-- Player 2 -->
        <div class="flex items-center gap-3" :class="{ 'opacity-50': !match.player2.win }">
          <img
            :src="`${DDRAGON}/${match.player2.champion}.png`"
            :alt="match.player2.champion"
            class="w-10 h-10 rounded-lg"
            @error="($event.target as HTMLImageElement).style.display = 'none'"
          />
          <div>
            <div class="font-medium text-sm">{{ player2.name }}</div>
            <div class="text-xs text-muted-foreground">{{ match.player2.champion }}</div>
            <div class="text-sm font-mono">
              {{ match.player2.kills }}/{{ match.player2.deaths }}/{{ match.player2.assists }}
            </div>
          </div>
          <Badge :variant="match.player2.win ? 'default' : 'secondary'" class="ml-auto text-xs">
            {{ match.player2.win ? 'Win' : 'Loss' }}
          </Badge>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
