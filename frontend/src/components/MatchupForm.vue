<script setup lang="ts">
import { ref, watch } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import RegionSelector from './RegionSelector.vue'

const emit = defineEmits<{
  search: [player1: string, player2: string, region: string]
}>()

const player1 = ref('')
const player2 = ref('')
const region = ref('europe')

const props = defineProps<{
  loading: boolean
  initialPlayer1?: string
  initialPlayer2?: string
  initialRegion?: string
}>()

watch(
  () => props.initialPlayer1,
  (value) => {
    if (value !== undefined) player1.value = value
  },
  { immediate: true },
)

watch(
  () => props.initialPlayer2,
  (value) => {
    if (value !== undefined) player2.value = value
  },
  { immediate: true },
)

watch(
  () => props.initialRegion,
  (value) => {
    if (value) region.value = value
  },
  { immediate: true },
)

function onSubmit() {
  if (!player1.value.includes('#') || !player2.value.includes('#')) return
  emit('search', player1.value.trim(), player2.value.trim(), region.value)
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="flex w-full flex-col gap-5">
    <div class="space-y-2">
      <label class="text-sm font-medium text-foreground">First Riot ID</label>
      <Input
        v-model="player1"
        placeholder="Faker#KR1"
        class="h-11 rounded-xl border-primary/15 bg-background/80"
        :disabled="loading"
      />
    </div>

    <div class="flex items-center gap-3 text-[11px] font-semibold uppercase tracking-[0.3em] text-primary/80">
      <div class="h-px flex-1 bg-gradient-to-r from-transparent via-primary/60 to-transparent" />
      <span>vs</span>
      <div class="h-px flex-1 bg-gradient-to-r from-transparent via-primary/60 to-transparent" />
    </div>

    <div class="space-y-2">
      <label class="text-sm font-medium text-foreground">Second Riot ID</label>
      <Input
        v-model="player2"
        placeholder="Caps#EUW"
        class="h-11 rounded-xl border-primary/15 bg-background/80"
        :disabled="loading"
      />
    </div>

    <div class="space-y-2">
      <label class="text-sm font-medium text-foreground">Region</label>
      <RegionSelector v-model="region" />
    </div>

    <Button
      type="submit"
      size="lg"
      class="mt-2 h-11 w-full rounded-xl"
      :disabled="loading || !player1.includes('#') || !player2.includes('#')"
    >
      <template v-if="loading">
        <LoaderCircle class="size-4 animate-spin" />
        Scouting...
      </template>
      <template v-else>Open Matchup Dossier</template>
    </Button>

    <p class="text-xs leading-relaxed text-muted-foreground">
      Shared games open with patch context, champion lines, and public links for deeper review.
    </p>
  </form>
</template>
