// caic and md documentation navigation, search, canonical URLs, and static publishing.
import { defineConfig } from "vitepress";
import llmstxt from "vitepress-plugin-llms";

const origin = "https://docs.caic.xyz";
export default defineConfig({
  title: "caic docs",
  description: "Run, review, and recover parallel coding tasks with caic and md.",
  cleanUrls: true,
  sitemap: { hostname: origin },
  lastUpdated: true,
  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
    ["link", { rel: "llms-index", type: "text/plain", href: "/llms.txt" }],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:image", content: `${origin}/screenshots/frontend/desktop/overview-light.webp` }],
    ["meta", { name: "twitter:card", content: "summary_large_image" }],
  ],
  transformHead({ pageData }) {
    const path = pageData.relativePath.replace(/(?:index)?\.md$/, "");
    return [
      ["link", { rel: "canonical", href: `${origin}/${path}` }],
      ["meta", { property: "og:url", content: `${origin}/${path}` }],
      ["meta", { property: "og:title", content: `${pageData.title || "caic and md"} | caic docs` }],
      [
        "meta",
        {
          property: "og:description",
          content: pageData.description || "Run, review, and recover parallel coding tasks with caic and md.",
        },
      ],
    ];
  },
  themeConfig: {
    logo: "/favicon.svg",
    siteTitle: "caic docs",
    nav: [
      { text: "caic", link: "/caic/" },
      { text: "md", link: "/md/" },
      { text: "Go Mode ↗", link: "https://docs.gomode.dev/" },
      { text: "Website ↗", link: "https://caic.xyz/" },
    ],
    sidebar: {
      "/caic/": [
        {
          text: "Start here",
          items: [
            { text: "Overview", link: "/caic/" },
            { text: "Installation", link: "/caic/installation" },
            { text: "Task workflow", link: "/caic/tasks" },
            { text: "Recovery and handoffs", link: "/caic/recovery" },
          ],
        },
        {
          text: "Connect and configure",
          items: [
            { text: "Configuration", link: "/caic/configuration" },
            { text: "GitHub", link: "/caic/github" },
            { text: "GitLab", link: "/caic/gitlab" },
            { text: "Voice", link: "/caic/voice" },
            { text: "MCP access", link: "/caic/mcp" },
            { text: "Go Mode on Android", link: "/caic/android" },
          ],
        },
        {
          text: "Understand the system",
          items: [
            { text: "Security", link: "/caic/security" },
            { text: "Architecture", link: "/caic/architecture" },
            { text: "Design", link: "/caic/design" },
          ],
        },
      ],
      "/md/": [
        {
          text: "Start here",
          items: [
            { text: "Overview", link: "/md/" },
            { text: "Installation", link: "/md/installation" },
            { text: "Commands", link: "/md/commands" },
          ],
        },
        {
          text: "Your containers",
          items: [
            { text: "Configuration", link: "/md/configuration" },
            { text: "Harnesses", link: "/md/harnesses" },
            { text: "Preinstalled tools", link: "/md/preinstalled-tools" },
            { text: "Tailscale", link: "/md/tailscale" },
            { text: "Security", link: "/md/security" },
          ],
        },
        {
          text: "Understand the system",
          items: [
            { text: "Architecture", link: "/md/architecture" },
            { text: "Design", link: "/md/design" },
          ],
        },
      ],
    },
    outline: [2, 3],
    socialLinks: [{ icon: "github", link: "https://github.com/caic-xyz" }],
    search: { provider: "local" },
    editLink: { pattern: "https://github.com/caic-xyz/docs.caic.xyz/edit/main/:path", text: "Improve this page" },
    footer: { message: "Your agents. Your machine.", copyright: "caic and md · Apache 2.0" },
  },
  srcExclude: ["**/AGENTS.md", "**/CLAUDE.md", "**/README.md"],
  vite: {
    logLevel: "warn",
    plugins: [llmstxt({ title: "caic docs", description: "User documentation for caic and md." })],
  },
});
