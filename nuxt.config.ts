// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // ── Compatibility ──────────────────────────────────────────────
  compatibilityDate: '2026-06-25',

  // ── Modules ────────────────────────────────────────────────────
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/color-mode',
    '@nuxtjs/i18n',
    '@nuxt/content',
    '@nuxt/image',
    '@nuxtjs/sitemap',
  ],

  // ── App & Base URL ─────────────────────────────────────────────
  app: {
    // baseURL injected via NUXT_APP_BASE_URL env var in CI (e.g. '/my-repo/')
    baseURL: process.env.NUXT_APP_BASE_URL || '/',
  },

  // ── i18n — Chinese / English bilingual ─────────────────────────
  i18n: {
    strategy: 'prefix',
    defaultLocale: 'zh',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'lang',
      alwaysRedirect: false,
    },
    locales: [
      { code: 'zh', iso: 'zh-CN', name: '中文' },
      { code: 'en', iso: 'en-US', name: 'English' },
    ],
    vueI18n: './i18n.config.ts',
  },

  // ── Content — Markdown-driven blog ─────────────────────────────
  content: {
    // Nuxt Content v3 uses collections; define them per locale
    locales: ['zh', 'en'],
    defaultLocale: 'zh',
  },

  // ── Color Mode — Dark / Light ──────────────────────────────────
  colorMode: {
    classSuffix: '',       // adds 'dark' / 'light' class, not 'dark-mode'
    preference: 'system',  // follow OS preference
    fallback: 'light',
  },

  // ── Image ──────────────────────────────────────────────────────
  image: {
    // Optimize images for static generation
    staticFilename: '[publicPath]/_ipx/[name]-[hash][ext]',
  },

  // ── Sitemap ────────────────────────────────────────────────────
  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || 'https://PmrALQ.github.io',
  },
  sitemap: {
    autoI18n: true,
  },

  // ── Nitro — Static Generation ──────────────────────────────────
  nitro: {
    prerender: {
      crawlLinks: true,
        failOnError: false,
      routes: ['/'],
    },
    output: {
      publicDir: '.output/public',
    },
  },

  // ── Global CSS ──────────────────────────────────────────────────
  css: ['~/assets/css/main.css'],

  // ── Devtools ───────────────────────────────────────────────────
  devtools: { enabled: true },

  // ── Typescript ─────────────────────────────────────────────────
  typescript: {
    strict: true,
    shim: false,
  },
})
