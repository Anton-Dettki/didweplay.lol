<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const model = defineModel<string>({ default: 'europe' })

const regions = [
  { value: 'europe', label: 'Europe', desc: 'EUW / EUNE / TR / RU' },
  { value: 'americas', label: 'Americas', desc: 'NA / BR / LAN / LAS / OCE' },
  { value: 'asia', label: 'Asia', desc: 'KR / JP' },
]
</script>

<template>
  <Select v-model="model">
    <SelectTrigger class="w-[200px]">
      <SelectValue placeholder="Select region" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem v-for="r in regions" :key="r.value" :value="r.value">
        <span class="font-medium">{{ r.label }}</span>
        <span class="ml-2 text-xs text-muted-foreground">{{ r.desc }}</span>
      </SelectItem>
    </SelectContent>
  </Select>
</template>
