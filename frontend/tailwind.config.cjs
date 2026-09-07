module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          900: '#152238',
          800: '#1c2e4a',
          700: '#243b5c',
          600: '#2f4f73',
        },
        accent: {
          DEFAULT: '#8b2942',
          light: '#a83250',
          muted: '#f3e8eb',
        },
        cyan: {
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
        },
        surface: {
          DEFAULT: '#f4f1ea',
          card: '#fffcf7',
          line: '#ddd6c8',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'Segoe UI', 'system-ui', 'sans-serif'],
        display: ['"IBM Plex Serif"', 'Georgia', 'serif'],
        mono: ['"IBM Plex Mono"', 'Consolas', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 0 rgba(21, 34, 56, 0.06), 0 2px 8px rgba(21, 34, 56, 0.04)',
      },
    }
  },
  plugins: [],
}
