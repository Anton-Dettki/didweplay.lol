<script setup lang="ts">
import { ref } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import RegionSelector from './RegionSelector.vue'

const emit = defineEmits<{
  search: [player: string, region: string]
}>()

const player = ref('')
const region = ref('europe')

defineProps<{ loading: boolean }>()

function onSubmit() {
  if (!player.value.includes('#')) return
  emit('search', player.value.trim(), region.value)
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="flex w-full flex-col gap-5">
    <div class="space-y-2">
      <label class="text-sm font-medium text-foreground">Summoner Riot ID</label>
      <Input
        v-model="player"
        placeholder="Faker#KR1"
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
      :disabled="loading || !player.includes('#')"
    >
      <template v-if="loading">
        <LoaderCircle class="size-4 animate-spin" />
        Sweeping match history...
      </template>
      <template v-else>Find Recurring Allies</template>
    </Button>

    <p class="text-xs leading-relaxed text-muted-foreground">
      This sweep walks the available match history and keeps fetched match details locally so later scans are faster.
    </p>
  </form>
</template>
