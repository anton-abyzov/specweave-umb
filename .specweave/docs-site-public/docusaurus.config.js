// @ts-check
// Auto-generated documentation site configuration
// Generated: 2026-02-22T04:59:30.512Z

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'specweave Documentation',
  tagline: 'Project Documentation',
  favicon: 'img/favicon.svg',

  // Production URL
  url: 'http://localhost',
  baseUrl: '/',

  onBrokenLinks: 'warn',
  onBrokenAnchors: 'warn',

  // Internationalization
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          path: '../docs/public',
          sidebarPath: './sidebars.js',
          editUrl: undefined,
          exclude: ['**/legacy/**', '**/node_modules/**', '**/_archive/**'],
          remarkPlugins: [],
          rehypePlugins: [],
          beforeDefaultRemarkPlugins: [],
          beforeDefaultRehypePlugins: [],
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'specweave Docs',
        logo: {
          alt: 'specweave Logo',
          src: 'img/logo.svg',
        },
        items: [],
      },

      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Academy',
                to: '/academy',
              },
              {
                label: 'API',
                to: '/api',
              },
              {
                label: 'Commands',
                to: '/commands',
              },
              {
                label: 'Development',
                to: '/development',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} specweave. Built with Docusaurus.`,
      },

      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'typescript', 'javascript', 'json', 'yaml'],
      },

      colorMode: {
        defaultMode: 'light',
        respectPrefersColorScheme: true,
      },
    }),

  // Mermaid diagrams support
  markdown: {
    mermaid: true,
    format: 'md',
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },
  themes: ['@docusaurus/theme-mermaid'],
};

export default config;
