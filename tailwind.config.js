/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './app.vue',
    './content/**/*.md',
  ],

  darkMode: 'class',

  theme: {
    extend: {
      colors: {
        // Apple accent — blue only
        primary: {
          50:  '#f0f7ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#0071e3',  // Apple blue
          700: '#0066cc',
          800: '#004499',
          900: '#002266',
          950: '#001133',
        },
        // Apple neutrals — grayscale body world
        apple: {
          bg:      '#f5f5f7',
          surface: '#ffffff',
          hover:   '#fbfbfd',
          text:    '#1d1d1f',
          body:    '#424245',
          muted:   '#6e6e73',
          subtle:  '#86868b',
          faint:   '#aeaeb2',
          line:    '#d2d2d7',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"', '"SF Pro Display"', '"Helvetica Neue"', '"PingFang SC"', '"Hiragino Sans GB"', '"Microsoft YaHei"', 'sans-serif'],
        mono: ['ui-monospace', '"SF Mono"', 'Menlo', '"Cascadia Code"', 'monospace'],
      },
      borderRadius: {
        chip:  '6px',
        thumb: '12px',
        sheet: '16px',
        card:  '18px',
        panel: '22px',
        hero:  '26px',
      },
      boxShadow: {
        'card':    '0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.05)',
        'panel':   '0 1px 3px rgba(0,0,0,0.05), 0 14px 40px rgba(0,0,0,0.05)',
        'lift':    '0 12px 32px rgba(0,0,0,0.10)',
        'cta':     '0 20px 54px rgba(0,113,227,0.24)',
        'overlay': '0 2px 8px rgba(0,0,0,0.10), 0 30px 80px rgba(0,0,0,0.24)',
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '72ch',
          },
        },
      },
      maxWidth: {
        read: '720px',
        grid: '1080px',
      },
      spacing: {
        pad: '22px',
      },
    },
  },

  plugins: [
    require('@tailwindcss/typography'),
  ],
}
