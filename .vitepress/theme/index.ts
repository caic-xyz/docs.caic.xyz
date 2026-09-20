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
    const wResp = await fetch(`https://discord.com/api/guilds/${DISCORD_GUILD_ID}/widget.json`);
    const wData = await wResp.json();
    const inviteCode = wData.instant_invite ? new URL(wData.instant_invite).pathname.split("/").pop() : null;
    let memberCount = 0;
    if (inviteCode) {
      const iResp = await fetch(`https://discord.com/api/invites/${inviteCode}?with_counts=true`);
      const iData = await iResp.json();
      memberCount = iData.approximate_member_count || 0;
    }
    document.querySelectorAll('a[href*="discord.gg/caic"], a[href*="discord.com/widget"]').forEach((a) => {
      const el = a as HTMLAnchorElement;
      const isWidgetLink = el.href.includes("discord.com/widget");
      if (wData.instant_invite) el.href = wData.instant_invite;
      if (isWidgetLink) {
        el.title = `${memberCount} members`;
        return;
      }
      const countText = memberCount > 0 ? ` (${memberCount} members)` : "";
      el.title = `${memberCount} members`;
      const orig = el.getAttribute("data-discord-orig-text");
      if (!orig) {
        el.setAttribute("data-discord-orig-text", el.textContent || "");
      }
      const base = orig || el.textContent || "";
      el.textContent = `${base}${countText}`;
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
    const initZoom = () => mediumZoom(".main img", { background: "var(--vp-c-bg)" });
    const initDiscord = () => updateDiscordLinks();
    onMounted(() => {
      initZoom();
      initDiscord();
    });
    watch(
      () => route.path,
      () =>
        nextTick(() => {
          initZoom();
          initDiscord();
        }),
    );
  },
};
