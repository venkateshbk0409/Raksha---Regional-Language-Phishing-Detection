/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Noto Sans Kannada', 'system-ui', '-apple-system', 'sans-serif'],
        kannada: ['Noto Sans Kannada', 'Inter', 'sans-serif'],
      },
      colors: {
        canvas: {
          50: '#fcfbf9',
          100: '#f6f5f0',
          200: '#efede6',
          300: '#e3e0d5',
          400: '#d0ccc0',
        },
        surface: {
          DEFAULT: '#faf9f5',
          card: '#ffffff',
          muted: '#f2f0e8',
          subtle: '#ebe8de',
        },
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#4f46e5',
          600: '#3730a3',
          700: '#312e81',
          800: '#1e1b4b',
          900: '#151336',
        },
        safe: {
          bg: '#ecf7ed',
          border: '#c3e6cb',
          text: '#14532d',
          accent: '#1b7a43',
          light: '#f4fbf5',
        },
        suspicious: {
          bg: '#fef6e7',
          border: '#fde1ab',
          text: '#783e08',
          accent: '#d97706',
          light: '#fffbf2',
        },
        phishing: {
          bg: '#fdf0ee',
          border: '#f9c6c0',
          text: '#881c1c',
          accent: '#c53030',
          light: '#fff7f6',
        },
      },
      boxShadow: {
        'soft': '0 2px 8px -2px rgba(28, 25, 23, 0.04), 0 8px 24px -4px rgba(28, 25, 23, 0.06)',
        'elevated': '0 4px 16px -2px rgba(28, 25, 23, 0.06), 0 12px 32px -4px rgba(28, 25, 23, 0.08)',
        'input': '0 2px 6px -1px rgba(28, 25, 23, 0.03)',
      }
    },
  },
  plugins: [],
};
