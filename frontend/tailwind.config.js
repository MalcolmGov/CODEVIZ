export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
        },
        'slate-canvas': '#030712',
        'slate-surface': '#090d16',
        'slate-elevated': '#0f172a',
        'slate-border': '#1f2937',
        'slate-borderLight': 'rgba(255, 255, 255, 0.06)',
      },
    },
  },
  plugins: [],
}

