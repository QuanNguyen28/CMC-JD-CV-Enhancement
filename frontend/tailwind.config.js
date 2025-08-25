import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0F172A',
        primary: '#4F8EF7',
        soft: '#EEF2FF'
      },
      boxShadow: {
        neo: '10px 10px 24px #e5e7eb, -10px -10px 24px #ffffff',
        ring: '0 8px 24px rgba(79,142,247,0.35)'
      },
      borderRadius: {
        xl2: '1rem'
      }
    }
  },
  plugins: [forms]
};