<script setup lang="ts">
import { ref } from 'vue'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import RegionSelector from './RegionSelector.vue'

const emit = defineEmits<{
  search: [player1: string, player2: string, region: string]
}>()

const player1 = ref('')
const player2 = ref('')
const region = ref('europe')

defineProps<{ loading: boolean }>()

function onSubmit() {
  if (!player1.value.includes('#') || !player2.value.includes('#')) return
  emit('search', player1.value.trim(), player2.value.trim(), region.value)
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="flex flex-col items-center gap-4 w-full max-w-md">
    <Input
      v-model="player1"
      placeholder="Player 1 (e.g. Faker#KR1)"
      class="text-center"
      :disabled="loading"
    />
    <div class="text-sm text-muted-foreground font-medium">vs</div>
    <Input
      v-model="player2"
      placeholder="Player 2 (e.g. Caps#EUW)"
      class="text-center"
      :disabled="loading"
    />
    <RegionSelector v-model="region" />
    <Button type="submit" class="w-full" :disabled="loading || !player1.includes('#') || !player2.includes('#')">
      <template v-if="loading">
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Searching...
      </template>
      <template v-else>Find Common Matches</template>
    </Button>
  </form>
</template>
