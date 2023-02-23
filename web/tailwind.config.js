/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './public/**/*.html',
    './src/**/*.{js,jsx,ts,tsx,vue}',
  ],
  darkMode: 'media',
  theme: {
    extend: {
      screens: {
        'slab': '480px',
      },
      colors: {
        primary: {
          '50': 'hsla(0, 0%, 95%, 1)',
          '800': 'hsla(0, 0%, 20%, 1)',
          '900': 'hsla(210, 0%, 10%, 1)',
        },
        login: {
          '50': 'hsla(120, 0%, 100%, 1)',
          '400': 'hsla(120, 95%, 50%, 1)',
          '500': 'hsla(120, 100%, 60%, 1)',
          '900': 'hsla(210, 5%, 16%, 1)',
        }
      },
    },
  },
  plugins: [],
}
