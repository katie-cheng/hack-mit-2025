'use client';

import Link from 'next/link';
import { Sparkles } from 'lucide-react';
import Button from '@/components/ui/Button';

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center" data-content="main">
      {/* Hero Section */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center mb-8">
            <svg 
              className="h-12 w-12 mr-2 silver-glow transform rotate-45" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="white" 
              strokeWidth="1"
              style={{ background: 'transparent' }}
            >
              <path d="M12 2L14.5 8.5L21 11L14.5 13.5L12 20L9.5 13.5L3 11L9.5 8.5L12 2Z" />
            </svg>
            <h1 className="text-6xl md:text-7xl text-display text-text-primary leading-tight">
              Mercury
            </h1>
          </div>
          <p className="text-xl md:text-2xl text-text-secondary mb-12 leading-relaxed subtitle-thin">
            Intelligent Home Energy Management
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link href="/register">
              <Button size="lg">
                Register Your Home
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="secondary" size="lg">
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}