import type { Metadata } from 'next'
import { IBM_Plex_Sans, Inria_Serif, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const ibmPlexSans = IBM_Plex_Sans({ 
  subsets: ['latin'],
  variable: '--font-ibm-plex-sans',
  weight: ['300', '400', '500', '600', '700'],
  display: 'swap',
})

const inriaSerif = Inria_Serif({ 
  subsets: ['latin'],
  variable: '--font-inria-serif',
  weight: ['300', '400', '700'],
  style: ['normal', 'italic'],
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-jetbrains',
  weight: ['300', '400', '500', '600'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Mercury - Intelligent Home Energy Management',
  description: 'Transform your home into an intelligent energy ecosystem',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${ibmPlexSans.variable} ${inriaSerif.variable} ${jetbrainsMono.variable} font-body antialiased`}>
        {children}
      </body>
    </html>
  )
}