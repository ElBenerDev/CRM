$tailwindConfig = @"
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.{html,js}',
    './app/static/**/*.{html,js}'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"@
Set-Content -Path "tailwind.config.js" -Value $tailwindConfigs