/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        arctic: {
          bg: '#0f172a',
          text: '#e2e8f0',
          accent: '#60a5fa',
          danger: '#ef4444',
          warning: '#f59e0b',
          success: '#10b981'
        },
        battle: {
          bg: '#1a0000',
          text: '#ffcccc',
          accent: '#ff3333',
          danger: '#ff0000'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      },
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        fadeIn: 'fadeIn 0.5s ease-in'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        }
      }
    }
  },
  plugins: []
}
