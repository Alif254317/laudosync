import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  theme: {
    extend: {
      colors: {
        // Cores do Elo System
        'elo-green': '#8BC34A',
        'elo-blue': '#2196F3',
        'elo-purple': '#5C2D91',
        // Status colors
        'concordancia': '#27ae60',
        'parcial': '#f39c12',
        'discordancia': '#e74c3c',
      }
    }
  }
}
