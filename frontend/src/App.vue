<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { Button } from '@/components/ui/button'
import {
  useMatchupCheck,
  useRepeatTeammatesCheck,
  type RepeatTeammate,
} from '@/lib/api'
import MatchupForm from '@/components/MatchupForm.vue'
import RepeatedTeammatesForm from '@/components/RepeatedTeammatesForm.vue'
import PlayerStats from '@/components/PlayerStats.vue'
import MatchList from '@/components/MatchList.vue'
import FrequentTeammatesList from '@/components/FrequentTeammatesList.vue'
import LoadingStatus from '@/components/LoadingStatus.vue'

type Mode = 'matchup' | 'teammates'
type RelationFilter = 'all' | 'same_team' | 'opponents'

const mode = ref<Mode>('matchup')
const resultsAnchor = ref<HTMLElement | null>(null)
const repeatTeammatesRegion = ref('europe')
const matchupInitialPlayer1 = ref('')
const matchupInitialPlayer2 = ref('')
const matchupInitialRegion = ref('europe')
const matchupInitialRelationFilter = ref<RelationFilter>('all')

const {
  loading: matchupLoading,
  progress: matchupProgress,
  result: matchupResult,
  error: matchupError,
  check: checkMatchup,
  checkPair: checkMatchupPair,
} = useMatchupCheck()
const {
  loading: repeatTeammatesLoading,
  progress: repeatTeammatesProgress,
  result: repeatTeammatesResult,
  error: repeatTeammatesError,
  check: checkRepeatTeammates,
} = useRepeatTeammatesCheck()

const anyLoading = computed(() => matchupLoading.value || repeatTeammatesLoading.value)
const activeLoading = computed(() => (
  mode.value === 'matchup' ? matchupLoading.value : repeatTeammatesLoading.value
))
const activeProgress = computed(() => {
  if (mode.value === 'matchup') {
    return matchupProgress.value || 'Checking shared matches...'
  }

  return repeatTeammatesProgress.value || 'Scanning match history for repeat teammates...'
})
const activeError = computed(() => (
  mode.value === 'matchup' ? matchupError.value : repeatTeammatesError.value
))

function formatRiotId(name: string, tag: string) {
  return tag ? `${name}#${tag}` : name
}

async function scrollToResults() {
  await nextTick()
  resultsAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function onMatchupSearch(player1: string, player2: string, region: string) {
  matchupInitialPlayer1.value = player1
  matchupInitialPlayer2.value = player2
  matchupInitialRegion.value = region
  matchupInitialRelationFilter.value = 'all'
  checkMatchup(player1, player2, region)
  void scrollToResults()
}

function onRepeatTeammatesSearch(player: string, region: string) {
  repeatTeammatesRegion.value = region
  checkRepeatTeammates(player, region)
  void scrollToResults()
}

function onOpenRepeatTeammate(teammate: RepeatTeammate) {
  const currentPlayer = repeatTeammatesResult.value?.player
  if (!currentPlayer?.puuid) return

  matchupInitialPlayer1.value = formatRiotId(currentPlayer.name, currentPlayer.tag)
  matchupInitialPlayer2.value = formatRiotId(teammate.name, teammate.tag)
  matchupInitialRegion.value = repeatTeammatesRegion.value
  matchupInitialRelationFilter.value = 'same_team'
  mode.value = 'matchup'

  checkMatchupPair({
    player1Name: currentPlayer.name,
    player1Tag: currentPlayer.tag,
    player1Puuid: currentPlayer.puuid,
    player2Name: teammate.name,
    player2Tag: teammate.tag,
    player2Puuid: teammate.puuid,
    region: repeatTeammatesRegion.value,
  })
  void scrollToResults()
}
</script>

<template>
  <div class="min-h-screen">
    <div class="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <section class="relative overflow-hidden rounded-[2rem] border border-primary/20 bg-card/90 shadow-[0_32px_110px_-56px_rgba(0,0,0,0.95)] backdrop-blur">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,195,77,0.18),transparent_32%),radial-gradient(circle_at_top_right,rgba(34,211,238,0.16),transparent_28%),radial-gradient(circle_at_bottom_center,rgba(8,47,73,0.35),transparent_42%)]" />
        <div class="absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-primary/80 to-transparent" />

        <div class="relative grid gap-8 px-6 py-8 lg:grid-cols-[1.15fr_0.85fr] lg:px-10 lg:py-10">
          <div class="space-y-6">
            <div class="inline-flex w-fit rounded-full border border-primary/30 bg-primary/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-primary">
              Did We Play Before
            </div>

            <div class="space-y-4">
              <h1 class="font-display text-4xl leading-none sm:text-5xl lg:text-6xl">
                Scout past clashes and familiar allies on the Rift.
              </h1>
              <p class="max-w-2xl text-base text-muted-foreground sm:text-lg">
                Build a quick dossier on any Riot ID matchup, or scan one summoner&apos;s history to uncover the teammates that keep reappearing across queues and patches.
              </p>
            </div>

            <div class="grid gap-3 sm:grid-cols-3">
              <div class="rounded-2xl border border-primary/15 bg-background/60 p-4">
                <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Scout Modes</div>
                <div class="mt-2 text-sm font-medium">Direct clash lookup or repeat ally scan</div>
              </div>
              <div class="rounded-2xl border border-primary/15 bg-background/60 p-4">
                <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Readout</div>
                <div class="mt-2 text-sm font-medium">Shared matches, recurring allies, patch-aware links</div>
              </div>
              <div class="rounded-2xl border border-primary/15 bg-background/60 p-4">
                <div class="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Routing</div>
                <div class="mt-2 text-sm font-medium">Europe, Americas, and Asia shards</div>
              </div>
            </div>
          </div>

          <div class="rounded-[1.75rem] border border-primary/20 bg-background/85 p-6 shadow-[0_30px_100px_-60px_rgba(0,0,0,1)] backdrop-blur">
            <div class="mb-5">
              <div class="inline-flex rounded-xl border border-primary/15 bg-muted/60 p-1">
                <Button
                  size="sm"
                  :variant="mode === 'matchup' ? 'default' : 'ghost'"
                  :disabled="anyLoading"
                  @click="mode = 'matchup'"
                >
                  Shared Matches
                </Button>
                <Button
                  size="sm"
                  :variant="mode === 'teammates' ? 'default' : 'ghost'"
                  :disabled="anyLoading"
                  @click="mode = 'teammates'"
                >
                  Repeat Teammates
                </Button>
              </div>

              <div class="mt-5 text-sm font-semibold uppercase tracking-[0.22em] text-primary">
                {{ mode === 'matchup' ? 'Shared Match Lookup' : 'Repeat Teammate Scan' }}
              </div>

              <p class="mt-2 text-sm text-muted-foreground">
                <template v-if="mode === 'matchup'">
                  Use the exact Riot ID format: <span class="font-medium text-foreground">Name#Tag</span>.
                  When they have crossed paths before, the report opens the exact match trail.
                </template>
                <template v-else>
                  Scan one summoner to find every ally they have queued with more than once. Large histories take longer, and fetched match details plus encountered players are cached locally to make later sweeps cheaper.
                </template>
              </p>
            </div>

            <MatchupForm
              v-if="mode === 'matchup'"
              :loading="matchupLoading"
              :initial-player1="matchupInitialPlayer1"
              :initial-player2="matchupInitialPlayer2"
              :initial-region="matchupInitialRegion"
              @search="onMatchupSearch"
            />

            <RepeatedTeammatesForm
              v-else
              :loading="repeatTeammatesLoading"
              @search="onRepeatTeammatesSearch"
            />
          </div>
        </div>
      </section>

      <div v-if="activeLoading" class="mt-6">
        <LoadingStatus :message="activeProgress" />
      </div>

      <div
        v-if="activeError"
        class="mt-6 rounded-2xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive shadow-sm"
      >
        {{ activeError }}
      </div>

      <div ref="resultsAnchor" />

      <template v-if="mode === 'matchup' && matchupResult">
        <div v-if="matchupResult.total_common === 0" class="mt-8 rounded-[1.75rem] border border-primary/15 bg-card/90 p-8 text-center shadow-sm backdrop-blur">
          <div class="text-xs font-semibold uppercase tracking-[0.24em] text-primary">
            No Recorded Clash
          </div>
          <h2 class="mt-3 font-display text-3xl">
            {{ matchupResult.player1.name }}#{{ matchupResult.player1.tag }} and {{ matchupResult.player2.name }}#{{ matchupResult.player2.tag }}
          </h2>
          <p class="mt-3 text-muted-foreground">
            No common matches were found on the selected routing shard.
          </p>
        </div>

        <div v-else class="mt-8 space-y-6">
          <PlayerStats :data="matchupResult" />
          <MatchList :data="matchupResult" :initial-relation-filter="matchupInitialRelationFilter" />
        </div>
      </template>

      <div v-if="mode === 'teammates' && repeatTeammatesResult" class="mt-8">
        <FrequentTeammatesList
          :data="repeatTeammatesResult"
          :disabled="anyLoading"
          @open-matchup="onOpenRepeatTeammate"
        />
      </div>
    </div>
  </div>
</template>
