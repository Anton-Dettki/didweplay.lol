<script setup lang="ts">
import { useMatchupCheck } from '@/lib/api'
import MatchupForm from '@/components/MatchupForm.vue'
import PlayerStats from '@/components/PlayerStats.vue'
import MatchList from '@/components/MatchList.vue'

const { loading, progress, result, error, check } = useMatchupCheck()

function onSearch(player1: string, player2: string, region: string) {
  check(player1, player2, region)
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <div class="mx-auto max-w-2xl px-4 py-12">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold tracking-tight">LoL Matchup Checker</h1>
        <p class="text-muted-foreground mt-2">
          Check if two players have ever played together or against each other
        </p>
      </div>

      <div class="flex justify-center mb-8">
        <MatchupForm :loading="loading" @search="onSearch" />
      </div>

      <!-- Progress -->
      <div v-if="loading && progress" class="text-center text-sm text-muted-foreground animate-pulse mb-6">
        {{ progress }}
      </div>

      <!-- Error -->
      <div v-if="error" class="rounded-lg bg-destructive/10 border border-destructive/20 text-destructive p-4 text-center text-sm mb-6">
        {{ error }}
      </div>

      <!-- Results -->
      <template v-if="result">
        <div v-if="result.total_common === 0" class="text-center text-muted-foreground py-8">
          No common matches found between
          <strong>{{ result.player1.name }}#{{ result.player1.tag }}</strong>
          and
          <strong>{{ result.player2.name }}#{{ result.player2.tag }}</strong>.
        </div>

        <template v-else>
          <div class="space-y-6">
            <PlayerStats :data="result" />
            <MatchList :data="result" />
          </div>
        </template>
      </template>
    </div>
  </div>
</template>
