<!-- Terminal recording loads on opening, pauses on closing, and disposes on navigation. -->
<script setup lang="ts">
import { ref, nextTick, onUnmounted } from "vue";
import type { Player } from "asciinema-player";
const props = defineProps<{ src: string; cols?: number; rows?: number }>();
const el = ref<HTMLDivElement>();
const error = ref("");
let player: Player | null = null;
let disposed = false;
let loaded = false;
async function toggle(event: Event) {
  if (!(event.target instanceof HTMLDetailsElement)) return;
  try {
    if (!event.target.open) {
      await player?.pause();
      return;
    }
    if (loaded) return;
    loaded = true;
    const { create } = await import("asciinema-player");
    await import("asciinema-player/dist/bundle/asciinema-player.css");
    await nextTick();
    if (disposed || !el.value || !event.target.open) {
      loaded = false;
      return;
    }
    player = create(props.src, el.value, { cols: props.cols ?? 120, rows: props.rows ?? 46, autoPlay: false });
  } catch (cause) {
    error.value = "The recording could not load. Download it using the link below.";
    console.error("Terminal recording failed", cause);
  }
}
onUnmounted(() => {
  disposed = true;
  player?.dispose();
});
</script>
<template>
  <details class="terminal-recording" @toggle="toggle">
    <summary>Play the terminal walkthrough</summary>
    <div ref="el" />
    <p v-if="error" role="alert">{{ error }}</p>
    <a :href="props.src">Download the recording</a>
  </details>
</template>
