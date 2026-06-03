// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

import icon from 'astro-icon';

export default defineConfig({
  site: 'https://python.openaq.org',
  integrations: [
    starlight({
      title: 'OpenAQ Python SDK',
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/openaq/openaq-python',
        },
      ],
      components: {
        Hero: './src/components/Hero.astro',
      },
      customCss: ['./src/assets/landing.css'],
      sidebar: [
        {
          label: 'Introduction',
          items: [
            { label: 'About', slug: 'introduction/about' },
            {
              label: 'Navigating the docs',
              slug: 'introduction/navigating-the-docs',
            },
            { label: 'Contributing', slug: 'introduction/contributing' },
          ],
        },
        {
          label: 'Getting started',
          items: [
            { label: 'Quick start', slug: 'getting-started/quick-start' },
            { label: 'Client', slug: 'getting-started/client' },
            { label: 'Pagination', slug: 'getting-started/pagination' },
            { label: 'Exceptions', slug: 'getting-started/exceptions' },
            { label: 'Responses', slug: 'getting-started/responses' },
            { label: 'Resources', slug: 'getting-started/resources' },
          ],
        },
        {
          label: 'Resources',
          items: [
            { label: 'Locations', slug: 'resources/locations' },
            { label: 'Sensors', slug: 'resources/sensors' },
            { label: 'Measurements', slug: 'resources/measurements' },
            { label: 'Licenses', slug: 'resources/licenses' },
            { label: 'Manufacturers', slug: 'resources/manufacturers' },
            { label: 'Instruments', slug: 'resources/instruments' },
            { label: 'Parameters', slug: 'resources/parameters' },
            { label: 'Providers', slug: 'resources/providers' },
            { label: 'Owners', slug: 'resources/owners' },
            { label: 'Countries', slug: 'resources/countries' },
          ],
        },
        {
          label: 'Advanced usage',
          items: [
            { label: 'Custom serialization', slug: 'advanced/json' },
            { label: 'Logging', slug: 'advanced/logging' },
            { label: 'Custom rate limiting', slug: 'advanced/rate-limiting' },
          ],
        },
        {
          label: 'Common workflows',
          items: [
            {
              label: 'Querying spatially',
              slug: 'guides/querying-spatially',
            },
            {
              label: 'Integrating with Pandas',
              slug: 'guides/pandas',
            },
            {
              label: 'Paging results',
              slug: 'guides/paging-results',
            },
            {
              label: 'Writing data to csv',
              slug: 'guides/write-to-csv',
            },
            {
              label: 'Querying measurements',
              slug: 'guides/querying-measurements',
            },

          ],
        },
        {
          label: 'Reference',
          items: [
            { label: 'Client', slug: 'reference/client' },
            { label: 'Exceptions', slug: 'reference/exceptions' },
          ],
        },
      ],
    }),
    icon({
      include: {
        mdi: ['emoticon-happy-outline', 'emoticon-sad-outline'],
      },
    }),
  ],
});
