<!-- Select the displayed capture and full-size link with the docs theme before hydration. -->
<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  light: string;
  dark: string;
  alt: string;
  width: number;
  height: number;
  mobileLight?: string;
  mobileDark?: string;
  mobileWidth?: number;
  mobileHeight?: number;
  priority?: "high";
}>();
const themes = ["light", "dark"] as const;
const captures = computed(() => {
  const mobile =
    props.mobileLight && props.mobileDark
      ? { light: props.mobileLight, dark: props.mobileDark, width: props.mobileWidth, height: props.mobileHeight }
      : null;
  return themes.flatMap((theme) => {
    const desktopCapture = {
      theme,
      src: props[theme],
      width: props.width,
      height: props.height,
      viewport: mobile ? "desktop" : null,
    };
    if (!mobile) return [desktopCapture];
    return [
      desktopCapture,
      { theme, src: mobile[theme], width: mobile.width, height: mobile.height, viewport: "mobile" },
    ];
  });
});
</script>

<template>
  <a
    v-for="capture in captures"
    :key="capture.src"
    class="docs-screenshot-link"
    :data-screenshot-theme="capture.theme"
    :data-screenshot-viewport="capture.viewport"
    :href="capture.src"
    target="_blank"
    rel="noopener"
  >
    <img
      class="docs-screenshot"
      :src="capture.src"
      :width="capture.width"
      :height="capture.height"
      :alt="alt"
      loading="lazy"
      decoding="async"
      :fetchpriority="priority"
    />
  </a>
</template>
