'use client';

import Link from 'next/link';
import { Home, BarChart3, Sparkles, Zap, Shield, Thermometer, Battery, DollarSign } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { useEffect, useState } from 'react';

export default function HomePage() {
  const [sparkles, setSparkles] = useState<Array<{ id: number; x: number; y: number; delay: number }>>([]);

  useEffect(() => {
    const generateSparkles = () => {
      const newSparkles = Array.from({ length: 20 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        delay: Math.random() * 3,
      }));
      setSparkles(newSparkles);
    };

    generateSparkles();
    const interval = setInterval(generateSparkles, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Sparkles */}
      {sparkles.map((sparkle) => (
        <div
          key={sparkle.id}
          className="sparkle"
          style={{
            left: `${sparkle.x}%`,
            top: `${sparkle.y}%`,
            animationDelay: `${sparkle.delay}s`,
          }}
        />
      ))}

      {/* Header */}
      <header className="relative z-10 bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="relative">
                <Home className="h-8 w-8 text-white mr-3 pulse-glow" />
                <Sparkles className="h-4 w-4 text-yellow-300 absolute -top-1 -right-1 animate-pulse" />
              </div>
              <h1 className="text-2xl font-bold gradient-text">AURA</h1>
            </div>
            <nav className="flex space-x-8">
              <Link href="/register" className="text-white/90 hover:text-white transition-colors duration-300 font-medium">
                Register Home
              </Link>
              <Link href="/dashboard" className="text-white/90 hover:text-white transition-colors duration-300 font-medium">
                EOC Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16">
          <div className="relative inline-block">
            <h2 className="text-5xl md:text-6xl font-bold text-white mb-6 floating">
              Smart Home Management System
            </h2>
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-lg blur opacity-30"></div>
          </div>
          <p className="text-xl text-white/90 max-w-3xl mx-auto leading-relaxed">
            Proactive AI system that protects your home from weather events. 
            Get intelligent alerts and automated responses to keep your home secure and profitable.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <Card className="text-center rainbow-border">
            <div className="flex justify-center mb-4">
              <div className="relative">
                <Thermometer className="h-8 w-8 text-blue-600" />
                <Zap className="h-4 w-4 text-yellow-400 absolute -top-1 -right-1 animate-bounce" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Weather Intelligence
            </h3>
            <p className="text-gray-600">
              AI analyzes weather patterns and proactively alerts you to potential 
              heatwaves, storms, and other events that could impact your home.
            </p>
          </Card>

          <Card className="text-center rainbow-border">
            <div className="flex justify-center mb-4">
              <div className="relative">
                <Battery className="h-8 w-8 text-green-600" />
                <Sparkles className="h-4 w-4 text-purple-400 absolute -top-1 -right-1 animate-pulse" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Automated Response
            </h3>
            <p className="text-gray-600">
              Smart systems automatically pre-cool your home, charge batteries, 
              and optimize energy usage to protect against weather events.
            </p>
          </Card>

          <Card className="text-center rainbow-border">
            <div className="flex justify-center mb-4">
              <div className="relative">
                <DollarSign className="h-8 w-8 text-orange-600" />
                <Zap className="h-4 w-4 text-red-400 absolute -top-1 -right-1 animate-ping" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Energy Trading
            </h3>
            <p className="text-gray-600">
              Automatically sell excess energy during peak demand periods, 
              turning weather events into profit opportunities.
            </p>
          </Card>
        </div>

        {/* CTA Sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card className="text-center rainbow-border pulse-glow">
            <div className="flex justify-center mb-4">
              <Home className="h-6 w-6 text-indigo-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              For Homeowners
            </h3>
            <p className="text-gray-600 mb-6">
              Register your home to receive intelligent weather alerts and automated protection.
            </p>
            <Link href="/register">
              <Button variant="primary" size="lg" className="w-full">
                <Sparkles className="h-4 w-4 mr-2" />
                Register Your Home
              </Button>
            </Link>
          </Card>

          <Card className="text-center rainbow-border pulse-glow">
            <div className="flex justify-center mb-4">
              <BarChart3 className="h-6 w-6 text-pink-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              EOC Dashboard
            </h3>
            <p className="text-gray-600 mb-6">
              Monitor your smart home systems and simulate weather events with our control center.
            </p>
            <Link href="/dashboard">
              <Button variant="secondary" size="lg" className="w-full">
                <Zap className="h-4 w-4 mr-2" />
                View Dashboard
              </Button>
            </Link>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 bg-white/10 backdrop-blur-md border-t border-white/20 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-white/80">
            <p>&copy; 2024 AURA. Built for HackMIT Hackathon.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
