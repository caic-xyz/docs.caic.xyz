// Documentation theme with an on-demand terminal recording component.
import DefaultTheme from "vitepress/theme-without-fonts";
import type { Theme } from "vitepress";
import { defineAsyncComponent } from "vue";
import ThemedScreenshot from "./ThemedScreenshot.vue";
import "./style.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("ThemedScreenshot", ThemedScreenshot);
    app.component(
      "AsciinemaPlayer",
      defineAsyncComponent(() => import("./AsciinemaPlayer.vue")),
    );
  },
} satisfies Theme;
