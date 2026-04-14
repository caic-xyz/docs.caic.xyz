<script setup lang="ts">
import { ref, onMounted } from "vue";

const props = defineProps<{ src: string; cols?: number; rows?: number }>();
const el = ref<HTMLDivElement>();

onMounted(async () => {
  const { create } = await import("asciinema-player");
  create(props.src, el.value!, {
    cols: props.cols ?? 120,
    rows: props.rows ?? 46,
    autoPlay: true,
    idleTimeLimit: 3,
    speed: 1,
  });
});
</script>

<template>
  <div ref="el" />
</template>
