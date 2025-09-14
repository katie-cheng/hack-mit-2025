/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        'display': ['var(--font-inria-serif)', 'serif'],
        'body': ['var(--font-ibm-plex-sans)', 'sans-serif'],
        'mono': ['var(--font-jetbrains)', 'monospace'],
      },
      colors: {
        // Mercury dark purple base colors
        mercury: {
          50: '#f4f3f7',   // Lightest purple-gray
          100: '#e8e6f0',  // Light purple-gray
          200: '#d1cce1',  // Soft purple-gray
          300: '#b4acd0',  // Medium purple-gray
          400: '#9187bb',  // Light purple
          500: '#7366a6',  // Medium purple
          600: '#5d5291',  // Rich purple
          700: '#4a4176',  // Deep purple
          800: '#1a0f2e',  // Dark purple 
          900: '#0f0a1a',  // Almost black purple (main bg)
        },
        
        // Silver/white accent colors
        silver: {
          50: '#ffffff',    // Pure white
          100: '#f8fafc',   // Off white
          200: '#f1f5f9',   // Light silver
          300: '#e2e8f0',   // Soft silver
          400: '#cbd5e1',   // Medium silver
          500: '#94a3b8',   // Rich silver
          600: '#64748b',   // Deep silver
          700: '#475569',   // Dark silver
          800: '#334155',   // Darker silver
          900: '#1e293b',   // Darkest silver
        },
        
        // Text colors for dark theme
        text: {
          primary: '#ffffff',    // Pure white
          secondary: '#f1f5f9',  // Light silver
          muted: '#cbd5e1',      // Medium silver
          inverse: '#3a325c',    // Dark purple
        },
        
        // Status colors with silver/purple tones
        status: {
          success: '#10b981',    // Emerald green
          warning: '#f59e0b',    // Amber
          danger: '#ef4444',     // Red
          info: '#3b82f6',       // Blue
        },
      },
      backgroundImage: {
        'mercury-grain': 'url("data:image/svg+xml,%3Csvg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noiseFilter"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" stitchTiles="stitch"/%3E%3C/filter%3E%3Crect width="100%25" height="100%25" filter="url(%23noiseFilter)" opacity="0.02"/%3E%3C/svg%3E")',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite alternate',
        'shimmer': 'shimmer 2s linear infinite',
        'mercury-pulse': 'mercuryPulse 3s ease-in-out infinite',
        'silver-shine': 'silverShine 0.3s ease-out',
        'shimmer-border': 'shimmerBorder 2s linear infinite',
        'liquid-flow': 'liquidFlow 0.5s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        pulseGlow: {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(148, 163, 184, 0.4)',
            transform: 'scale(1)'
          },
          '50%': { 
            boxShadow: '0 0 30px rgba(148, 163, 184, 0.6)',
            transform: 'scale(1.02)'
          },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        mercuryPulse: {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(148, 163, 184, 0.4)',
            transform: 'scale(1)'
          },
          '50%': { 
            boxShadow: '0 0 30px rgba(148, 163, 184, 0.6)',
            transform: 'scale(1.02)'
          },
        },
        silverShine: {
          '0%': { transform: 'rotateY(0deg)', filter: 'brightness(1)' },
          '50%': { transform: 'rotateY(-5deg)', filter: 'brightness(1.1)' },
          '100%': { transform: 'rotateY(0deg)', filter: 'brightness(1)' },
        },
        liquidFlow: {
          '0%': { 
            transform: 'scale(0.95)',
            opacity: '0.8'
          },
          '100%': { 
            transform: 'scale(1)',
            opacity: '1'
          },
        },
        shimmerBorder: {
          '0%': { 
            'border-color': 'rgba(148, 163, 184, 0.3)',
            'box-shadow': '0 0 5px rgba(148, 163, 184, 0.2)'
          },
          '50%': { 
            'border-color': 'rgba(148, 163, 184, 0.8)',
            'box-shadow': '0 0 20px rgba(148, 163, 184, 0.4)'
          },
          '100%': { 
            'border-color': 'rgba(148, 163, 184, 0.3)',
            'box-shadow': '0 0 5px rgba(148, 163, 184, 0.2)'
          },
        },
      },
      boxShadow: {
        'mercury': '0 1px 3px rgba(0, 0, 0, 0.2), 0 1px 2px rgba(93, 82, 145, 0.1)',
        'mercury-hover': '0 4px 6px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(93, 82, 145, 0.2)',
        'mercury-pressed': '0 1px 2px rgba(0, 0, 0, 0.3)',
        'silver-glow': '0 0 20px rgba(148, 163, 184, 0.4), 0 0 40px rgba(148, 163, 184, 0.2)',
      },
    },
  },
  plugins: [],
}