// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Lokyy Workspace documentation — Astro Starlight.
// Brand: Cyan #22D3EE → Blue #2563EB. Light + Dark.
export default defineConfig({
  site: 'https://aiianer.de',
  integrations: [
    starlight({
      title: 'Lokyy Workspace',
      description: 'The self-hosted AI operating system for the self-employed and SMEs.',
      logo: { src: './src/assets/lokyy-logo.png', alt: 'Lokyy' },
      social: {
        github: 'https://github.com/oliverhees/lokyy-workspace',
        youtube: 'https://youtube.com/@aiianer',
      },
      defaultLocale: 'root',
      locales: {
        root: { label: 'Deutsch', lang: 'de' },
        en: { label: 'English', lang: 'en' },
      },
      sidebar: [
        { label: 'Start', items: [
          { label: 'Überblick', slug: 'index' },
          { label: 'Erste Schritte', slug: 'getting-started' },
        ]},
        { label: 'Architektur', autogenerate: { directory: 'architecture' } },
        { label: 'Meilensteine', autogenerate: { directory: 'milestones' } },
      ],
    }),
  ],
});
