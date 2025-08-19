// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        surface: '#e9edf5',   // soft surface for neumorphism
        accent: '#4F46E5',    // indigo-600
        ink: '#111827'        // cool gray-900
      },
      boxShadow: {
        neo: '9px 9px 16px #c8ccd6, -9px -9px 16px #ffffff',
        neoin: 'inset 9px 9px 16px #c8ccd6, inset -9px -9px 16px #ffffff'
      },
      borderRadius: {
        xl2: '1.25rem'
      }
    }
  },
  plugins: []
}
