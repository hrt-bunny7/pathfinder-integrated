import type { Config } from 'tailwindcss';
const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#101936', paper: '#F5F7FB', line: '#DCE2EE',
        brand: { DEFAULT: '#2F54EB', dark: '#2441C0', soft: '#E6ECFF' },
        good: { DEFAULT: '#12A150', dark: '#0B7A3B', soft: '#E0F5E9' },
        amber: { DEFAULT: '#FF9F1C', dark: '#8A5300', soft: '#FFF1DB' },
        rust: { DEFAULT: '#D93F2B', soft: '#FDE9E5' },
      },
      fontFamily: { display: ['var(--font-display)', 'sans-serif'], sans: ['var(--font-body)', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [],
};
export default config;
