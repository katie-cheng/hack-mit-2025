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
        <script dangerouslySetInnerHTML={{
          __html: `
            let mouseX = 0;
            let mouseY = 0;
            let isMouseActive = false;
            let grainParticles = [];
            
            // Create grain particles around cursor
            function createGrainParticles(x, y) {
              // Remove old particles
              grainParticles.forEach(particle => {
                if (particle.element && particle.element.parentNode) {
                  particle.element.classList.add('fade-out');
                  setTimeout(() => {
                    if (particle.element && particle.element.parentNode) {
                      particle.element.parentNode.removeChild(particle.element);
                    }
                  }, 200);
                }
              });
              grainParticles = [];
              
              // Create new particles in a circle around cursor
              const radius = 80;
              const particleCount = 15;
              
              for (let i = 0; i < particleCount; i++) {
                const angle = (i / particleCount) * Math.PI * 2;
                const distance = Math.random() * radius;
                const particleX = x + Math.cos(angle) * distance + (Math.random() - 0.5) * 20;
                const particleY = y + Math.sin(angle) * distance + (Math.random() - 0.5) * 20;
                
                const particle = document.createElement('div');
                particle.className = 'cursor-grain-particle';
                particle.style.left = particleX + 'px';
                particle.style.top = particleY + 'px';
                particle.style.opacity = Math.random() * 0.8 + 0.2;
                
                // Vary particle size
                const size = Math.random() * 2 + 1;
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                
                document.body.appendChild(particle);
                grainParticles.push({ element: particle });
              }
            }
            
            let lastUpdate = 0;
            document.addEventListener('mousemove', (e) => {
              mouseX = e.clientX;
              mouseY = e.clientY;
              isMouseActive = true;
              
              const now = Date.now();
              if (now - lastUpdate > 50) { // Throttle to 20fps
                createGrainParticles(mouseX, mouseY);
                lastUpdate = now;
              }
            });
            
            // Remove particles when cursor leaves window
            document.addEventListener('mouseleave', () => {
              isMouseActive = false;
              grainParticles.forEach(particle => {
                if (particle.element && particle.element.parentNode) {
                  particle.element.classList.add('fade-out');
                  setTimeout(() => {
                    if (particle.element && particle.element.parentNode) {
                      particle.element.parentNode.removeChild(particle.element);
                    }
                  }, 200);
                }
              });
              grainParticles = [];
            });
          `
        }} />
      </body>
    </html>
  )
}