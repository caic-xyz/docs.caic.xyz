import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'caic-xyz docs',
  description: 'Documentation for caic and md',
  cleanUrls: true,

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    ['script', {}, `fetch('https://discord.com/api/guilds/1475502872564338822/widget.json')
      .then(r=>r.json()).then(d=>{if(d.instant_invite){
        document.querySelectorAll('a[href*="discord.com/widget"]').forEach(a=>a.href=d.instant_invite)
      }}).catch(()=>{})`],
  ],

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
            { text: 'Configuration', link: '/caic/configuration' },
            { text: 'GitHub Integration', link: '/caic/github' },
            { text: 'GitLab Integration', link: '/caic/gitlab' },
            { text: 'Android App', link: '/caic/android' },
            { text: 'Architecture', link: '/caic/architecture' },
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
      { icon: 'discord', link: 'https://discord.com/widget?id=1475502872564338822' },
      { icon: 'github', link: 'https://github.com/caic-xyz' },
    ],

    search: {
      provider: 'local',
    },
  },
})
