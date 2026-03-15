import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'caic-xyz docs',
  description: 'Documentation for caic and md',
  cleanUrls: true,

  themeConfig: {
    nav: [
      { text: 'caic', link: '/caic/' },
      { text: 'md', link: '/md/' },
    ],

    sidebar: {
      '/caic/': [
        {
          text: 'caic',
          items: [
            { text: 'Overview', link: '/caic/' },
            { text: 'Installation', link: '/caic/installation' },
            { text: 'Architecture', link: '/caic/architecture' },
            { text: 'Configuration', link: '/caic/configuration' },
            { text: 'Forge Integration', link: '/caic/forge' },
            { text: 'Android App', link: '/caic/android' },
          ],
        },
      ],
      '/md/': [
        {
          text: 'md',
          items: [
            { text: 'Overview', link: '/md/' },
            { text: 'Installation', link: '/md/installation' },
            { text: 'Commands', link: '/md/commands' },
            { text: 'Configuration', link: '/md/configuration' },
            { text: 'Harnesses', link: '/md/harnesses' },
            { text: 'Tailscale', link: '/md/tailscale' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/caic-xyz' },
    ],

    search: {
      provider: 'local',
    },
  },
})
