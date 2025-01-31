$postcssConfig = @"
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
"@
Set-Content -Path "postcss.config.js" -Value $postcssConfig