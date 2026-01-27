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
                label: 'About',
                items: [
                    {label: 'About', slug : 'about/about'},
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
                    {label: 'Locations', slug : 'getting-started/locations'},
                    {label: 'Sensors', slug : 'getting-started/sensors'},
                    {label: 'Measurements', slug : 'getting-started/measurements'},
                    {label: 'Licenses', slug : 'getting-started/licenses'},
                    {label: 'Manufacturers', slug : 'getting-started/manufacturers'},
                    {label: 'Instruments', slug : 'getting-started/instruments'},
                    {label: 'Parameters', slug : 'getting-started/parameters'},
                    {label: 'Providers', slug : 'getting-started/providers'},
                    {label: 'Owners', slug : 'getting-started/owners'},
                    {label: 'Countries', slug : 'getting-started/countries'},

                ],
            },
                            {
                label: 'Advanced',
                items: [
                    {label: 'Custom serialization', slug : 'advanced/json'},

                ],
            },
            {
                label: 'Guides',
                items: [
                    {label: 'Integrating with Pandas', slug : 'guides/pandas'},

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