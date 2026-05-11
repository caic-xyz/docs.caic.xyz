// VitePress theme with medium-zoom and Asciinema player.
import DefaultTheme from "vitepress/theme";
import mediumZoom from "medium-zoom";
import { onMounted, watch, nextTick } from "vue";
import { useRoute } from "vitepress";

import "asciinema-player/dist/bundle/asciinema-player.css";
import "./style.css";

import AsciinemaPlayer from "./AsciinemaPlayer.vue";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("AsciinemaPlayer", AsciinemaPlayer);
  },
  setup() {
    const route = useRoute();
    const initZoom = () =>
      mediumZoom(".main img", { background: "var(--vp-c-bg)" });
    onMounted(initZoom);
    watch(() => route.path, () => nextTick(initZoom));
  },
};
