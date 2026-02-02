// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

import icon from 'astro-icon';

// https://astro.build/config
export default defineConfig({
        site: 'https://openaq.github.io',
    base: '/openaq-python',
    integrations: [starlight({
        title: 'OpenAQ Python SDK',
        social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/openaq/openaq-python' }],
        components: {
				Hero: './src/components/Hero.astro',
	    },
        customCss: ['./src/assets/landing.css'],
        sidebar: [
                                            {
                label: 'Introduction',
                items: [
                    {label: 'About', slug : 'introduction/about'},
                    {label: 'Navigating the docs', slug : 'introduction/navigating-the-docs'},
                    {label: 'Contributing', slug : 'introduction/contributing'},
                ]},
                            {
                label: 'Getting started',
                items: [

                    {label: 'Quick start', slug : 'getting-started/quick-start'},
                    {label: 'Client', slug : 'getting-started/client'},
                    {label: 'Pagination', slug : 'getting-started/pagination'},
                    {label: 'Exceptions', slug : 'getting-started/exceptions'},
                    {label: 'Responses', slug : 'getting-started/responses'},
                    {label: 'Resources', slug : 'getting-started/resources'},

                ],
            },
                            {
                label: 'Working with resources',
                items: [
                    {label: 'Locations', slug : 'working-with-resources/locations'},
                    {label: 'Sensors', slug : 'working-with-resources/sensors'},
                    {label: 'Measurements', slug : 'working-with-resources/measurements'},
                    {label: 'Licenses', slug : 'working-with-resources/licenses'},
                    {label: 'Manufacturers', slug : 'working-with-resources/manufacturers'},
                    {label: 'Instruments', slug : 'working-with-resources/instruments'},
                    {label: 'Parameters', slug : 'working-with-resources/parameters'},
                    {label: 'Providers', slug : 'working-with-resources/providers'},
                    {label: 'Owners', slug : 'working-with-resources/owners'},
                    {label: 'Countries', slug : 'working-with-resources/countries'},

                ],
            },
                            {
                label: 'Advanced usage',
                items: [
                    {label: 'Custom serialization', slug : 'advanced-usage/json'},
                    {label: 'Logging', slug : 'advanced-usage/logging'},
                    {label: 'Custom rate limiting', slug : 'advanced-usage/rate-limiting'},
                ],
            },
            {
                label: 'Common workflows',
                items: [
                    {label: 'Integrating with Pandas', slug : 'common-workflows/pandas'},
                    {label: 'Querying around a city', slug : 'common-workflows/querying-around-a-city'},
                ],
            },
            {
                label: 'Reference',
                items: [
                    {label: 'Client', slug : 'reference/client'},
                    {label: 'Exceptions', slug : 'reference/exceptions'},
                ]
            },
        ],
		}
    ),
        
        icon()],
        
});