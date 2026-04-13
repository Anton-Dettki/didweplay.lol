<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'

defineProps<{ message: string }>()
</script>

<template>
  <div class="flex items-center gap-3 rounded-2xl border border-primary/20 bg-card/85 px-4 py-3 text-sm text-muted-foreground shadow-sm backdrop-blur">
    <LoaderCircle class="size-4 animate-spin text-primary" />
    <span>{{ message }}</span>
  </div>
</template>
