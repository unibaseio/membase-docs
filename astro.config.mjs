import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://docs.membase.io',
  integrations: [
    starlight({
      title: 'Membase Docs',
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/unibaseio/unibase-membase' }],
      sidebar: [
        { label: 'Overview', link: '/' },
        { label: 'Get Started', items: [{ slug: 'quick-start' }, { slug: 'integration-options' }] },
        {
          label: 'Concepts',
          items: ['architecture', 'identity', 'authorization', 'memory', 'cooperation', 'settlement', 'storage-backends']
            .map((slug) => ({ slug })),
        },
        { label: 'Reference', items: ['sdk-reference', 'hub', 'troubleshooting', 'faq'].map((slug) => ({ slug })) },
        {
          label: 'Resources',
          items: [
            { label: 'Membase Hub', link: 'https://hub.membase.unibase.com' },
            { label: 'Unibase Memory (Chrome extension)', link: 'https://docs.unibase.com/unibase-memory/' },
            { label: 'Unibase Docs', link: 'https://docs.unibase.com' },
          ],
        },
      ],
    }),
  ],
});
