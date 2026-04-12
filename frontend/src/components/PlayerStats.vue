<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { MatchupResult } from '@/lib/api'

const props = defineProps<{ data: MatchupResult }>()

const p1WinRate = computed(() => {
  if (!props.data.total_common) return 0
  return Math.round((props.data.stats.player1_wins / props.data.total_common) * 100)
})

const p2WinRate = computed(() => {
  if (!props.data.total_common) return 0
  return Math.round((props.data.stats.player2_wins / props.data.total_common) * 100)
})
</script>

<template>
  <Card class="w-full">
    <CardHeader>
      <CardTitle class="text-center">Head-to-Head Summary</CardTitle>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <div class="text-2xl font-bold">{{ data.total_common }}</div>
          <div class="text-sm text-muted-foreground">Games Together</div>
        </div>
        <div>
          <div class="text-2xl font-bold">{{ data.stats.same_team }}</div>
          <div class="text-sm text-muted-foreground">Same Team</div>
        </div>
        <div>
          <div class="text-2xl font-bold">{{ data.stats.opponents }}</div>
          <div class="text-sm text-muted-foreground">Opponents</div>
        </div>
      </div>
      <div class="mt-6 grid grid-cols-2 gap-4">
        <div class="rounded-lg bg-muted p-4 text-center">
          <div class="text-sm font-medium text-muted-foreground">{{ data.player1.name }}#{{ data.player1.tag }}</div>
          <div class="text-xl font-bold mt-1">{{ p1WinRate }}%</div>
          <div class="text-xs text-muted-foreground">{{ data.stats.player1_wins }}W / {{ data.total_common - data.stats.player1_wins }}L</div>
        </div>
        <div class="rounded-lg bg-muted p-4 text-center">
          <div class="text-sm font-medium text-muted-foreground">{{ data.player2.name }}#{{ data.player2.tag }}</div>
          <div class="text-xl font-bold mt-1">{{ p2WinRate }}%</div>
          <div class="text-xs text-muted-foreground">{{ data.stats.player2_wins }}W / {{ data.total_common - data.stats.player2_wins }}L</div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
