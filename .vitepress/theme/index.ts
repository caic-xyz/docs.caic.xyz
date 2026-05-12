// VitePress theme with medium-zoom and Asciinema player.
import DefaultTheme from "vitepress/theme";
import mediumZoom from "medium-zoom";
import { onMounted, watch, nextTick } from "vue";
import { useRoute } from "vitepress";

import "asciinema-player/dist/bundle/asciinema-player.css";
import "./style.css";

import AsciinemaPlayer from "./AsciinemaPlayer.vue";

const DISCORD_GUILD_ID = "1475502872564338822";

async function updateDiscordLinks() {
  try {
    const resp = await fetch(
      `https://discord.com/api/guilds/${DISCORD_GUILD_ID}/widget.json`,
    );
    const data = await resp.json();
    const count = data.presence_count || 0;
    document
      .querySelectorAll('a[href*="discord.gg/caic"]')
      .forEach((a) => {
        const el = a as HTMLAnchorElement;
        if (data.instant_invite) el.href = data.instant_invite;
        el.title = `${count} members online`;
        const orig = el.getAttribute("data-discord-orig-text");
        if (!orig) {
          el.setAttribute("data-discord-orig-text", el.textContent || "");
        }
        const base = orig || el.textContent || "";
        el.textContent = `${base} (${count} online)`;
      });
  } catch {
    // Discord API unreachable; links fall back to discord.gg/caic
  }
}

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("AsciinemaPlayer", AsciinemaPlayer);
  },
  setup() {
    const route = useRoute();
    const initZoom = () =>
      mediumZoom(".main img", { background: "var(--vp-c-bg)" });
    const initDiscord = () => updateDiscordLinks();
    onMounted(() => {
      initZoom();
      initDiscord();
    });
    watch(
      () => route.path,
      () => nextTick(() => {
        initZoom();
        initDiscord();
      }),
    );
  },
};
