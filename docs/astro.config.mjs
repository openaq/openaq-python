// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'OpenAQ Python SDK',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/openaq/openaq-python' }],
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
						{label: 'Geospatial queries', slug : 'getting-started/geospatial-queries'},
						{label: 'Responses', slug : 'getting-started/responses'},
						{label: 'Locations', slug : 'getting-started/locations'},
						{label: 'Sensors', slug : 'getting-started/sensors'},
						{label: 'Measurements', slug : 'getting-started/measurements'},
						{label: 'Manufacturers', slug : 'getting-started/manufacturers'},
						{label: 'Instruments', slug : 'getting-started/instruments'},
						{label: 'Parameters', slug : 'getting-started/parameters'},
						{label: 'Providers', slug : 'getting-started/providers'},
						{label: 'Exceptions', slug : 'getting-started/exceptions'},

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

					],
				},
				{
					label: 'Reference',
					items: [
						{label: 'Exceptions', slug : 'reference/exceptions'},
						{label: 'Locations', slug : 'reference/locations'},
						{label: 'Measurements', slug: 'reference/measurements'}
					]
				},
			],
		}),
	],
});
