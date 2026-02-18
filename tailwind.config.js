/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        void: '#050505',
        primary: '#E0E0E0',
        'accent-signal': '#FF4D00',
        'border-dim': 'rgba(255,255,255,0.1)',
      },
      fontFamily: {
        heading: ['"Space Mono"', '"Courier New"', 'monospace'],
        body: ['Inter', 'Helvetica', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        hud: '0 0 24px rgba(255, 77, 0, 0.25)',
      },
    },
  },
  plugins: [],
}
