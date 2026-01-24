/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./ampower_kj/public/js/**/*.{vue,js,jsx}",
    "./ampower_kj/ampower_keerti_pristine_jewels/page/**/*.{js,html}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors
        primary: {
          DEFAULT: '#0066b3',
          dark: '#005291',
          50: '#e1f5fe',
          100: '#b3e5fc',
          200: '#81d4fa',
          300: '#4fc3f7',
          400: '#29b6f6',
          500: '#03a9f4',
          600: '#039be5',
          700: '#0288d1',
          800: '#0277bd',
          900: '#01579b',
        },
        'primary-dark': '#005291',
        'background-light': '#F3F4F6',
        'background-dark': '#111827',
        'surface-light': '#FFFFFF',
        'surface-dark': '#1F2937',
        'surface-alt-light': '#F9FAFB',
        'surface-alt-dark': '#161e2e',
        // Status colors
        status: {
          unassigned: '#f59e0b',
          assigned: '#3b82f6',
          incoming: '#8b5cf6',
          qa: '#06b6d4',
          ready: '#10b981',
          delivered: '#22c55e',
          cancelled: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
        body: ['Outfit', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
        'dropdown': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'pulse-dot': 'pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'pulse-dot': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        }
      }
    },
  },
  plugins: [],
  // Prefix to avoid conflicts with Frappe's Bootstrap styles
  prefix: 'tw-',
  // Important to ensure Tailwind styles take precedence
  important: true,
}
