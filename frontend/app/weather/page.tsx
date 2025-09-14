'use client';

import { useState, useEffect } from 'react';
import { Thermometer, Zap, DollarSign, AlertTriangle, Newspaper, Play, Sun, Cloud, Wind } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

interface WeatherData {
  temperature: number;
  heatIndex: number;
  nextPeak: number;
  nwsWarning: string;
}

interface GridData {
  demand: number;
  reserveMargin: number;
  price: number;
  status: string;
}

interface NewsItem {
  id: number;
  title: string;
  source: string;
  timestamp: string;
  urgency: 'breaking' | 'alert' | 'status';
}

interface ThreatLevel {
  level: string;
  score: number;
  color: string;
}

export default function WeatherDashboard() {
  const [weatherData, setWeatherData] = useState<WeatherData>({
    temperature: 98,
    heatIndex: 105,
    nextPeak: 102,
    nwsWarning: 'Heat Advisory'
  });

  const [gridData, setGridData] = useState<GridData>({
    demand: 73420,
    reserveMargin: 3850,
    price: 185,
    status: 'Normal'
  });

  const [newsItems, setNewsItems] = useState<NewsItem[]>([
    {
      id: 1,
      title: "ERCOT issues conservation alert as Texas electricity demand approaches record high",
      source: "Austin American-Statesman",
      timestamp: "2 minutes ago",
      urgency: 'breaking'
    },
    {
      id: 2,
      title: "Austin-Travis County declares heat emergency, cooling centers open",
      source: "City of Austin",
      timestamp: "8 minutes ago",
      urgency: 'alert'
    },
    {
      id: 3,
      title: "Austin Energy requests immediate conservation as grid nears capacity",
      source: "Austin Energy Twitter",
      timestamp: "12 minutes ago",
      urgency: 'status'
    }
  ]);

  const [threatLevel, setThreatLevel] = useState<ThreatLevel>({
    level: 'MODERATE',
    score: 4,
    color: 'text-yellow-400'
  });

  // Simulate streaming data
  useEffect(() => {
    const interval = setInterval(() => {
      setWeatherData(prev => ({
        ...prev,
        temperature: Math.max(95, Math.min(110, prev.temperature + (Math.random() - 0.5) * 2)),
        heatIndex: Math.max(100, Math.min(120, prev.heatIndex + (Math.random() - 0.5) * 3)),
        nextPeak: Math.max(98, Math.min(108, prev.nextPeak + (Math.random() - 0.5) * 1.5)),
      }));

      setGridData(prev => ({
        ...prev,
        demand: Math.max(65000, Math.min(80000, prev.demand + (Math.random() - 0.5) * 500)),
        reserveMargin: Math.max(2000, Math.min(5000, prev.reserveMargin + (Math.random() - 0.5) * 200)),
        price: Math.max(50, Math.min(300, prev.price + (Math.random() - 0.5) * 20)),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Calculate threat level
  useEffect(() => {
    let score = 0;
    if (weatherData.temperature > 105) score += 2;
    if (weatherData.heatIndex > 110) score += 2;
    if (gridData.demand > 75000) score += 2;
    if (gridData.reserveMargin < 3000) score += 3;
    if (gridData.price > 200) score += 1;
    if (weatherData.nwsWarning === 'Heat Warning') score += 1;

    let level = 'LOW';
    let color = 'text-green-400';
    
    if (score >= 3 && score <= 5) {
      level = 'MODERATE';
      color = 'text-yellow-400';
    } else if (score >= 6 && score <= 8) {
      level = 'HIGH';
      color = 'text-orange-400';
    } else if (score >= 9) {
      level = 'CRITICAL';
      color = 'text-red-400';
    }

    setThreatLevel({ level, score, color });
  }, [weatherData, gridData]);

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'breaking': return 'text-red-400';
      case 'alert': return 'text-yellow-400';
      case 'status': return 'text-blue-400';
      default: return 'text-text-secondary';
    }
  };

  const getUrgencyLabel = (urgency: string) => {
    switch (urgency) {
      case 'breaking': return 'BREAKING';
      case 'alert': return 'HEAT ALERT';
      case 'status': return 'GRID STATUS';
      default: return 'UPDATE';
    }
  };

  return (
    <div className="min-h-screen p-4" data-content="main">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 pt-8">
          <h1 className="text-4xl font-bold text-display text-text-primary mb-4">
            Austin Weather & Grid Dashboard
          </h1>
          <p className="text-lg text-body text-text-secondary font-light max-w-3xl mx-auto mb-6">
            Real-time monitoring of weather conditions and grid stability for emergency response coordination.
          </p>
          
          {/* Threat Level Indicator */}
          <div className="inline-flex items-center gap-3 mb-8">
            <AlertTriangle className={`h-6 w-6 ${threatLevel.color}`} />
            <div className="text-left">
              <div className={`text-xl font-bold ${threatLevel.color}`}>
                THREAT LEVEL: {threatLevel.level}
              </div>
              <div className="text-sm text-text-muted">
                Risk Score: {threatLevel.score}/12
              </div>
            </div>
          </div>

          {/* Start Demo Button - Centered below threat assessment */}
          <div className="flex justify-center mb-8">
            <Button 
              size="lg" 
              className="px-8 py-4 text-lg flex items-center gap-3"
              onClick={() => window.location.href = '/dashboard'}
            >
              <Play className="h-5 w-5" />
              Start Demo
            </Button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Weather Metrics */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-heading text-text-primary mb-4">
              Weather Conditions
            </h2>
            
            {/* Current Temperature */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">Current Temperature</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {Math.round(weatherData.temperature)}°F
                  </p>
                </div>
                <div className="relative">
                  <Thermometer className="h-8 w-8 text-orange-400 animate-pulse" />
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full animate-ping"></div>
                </div>
              </div>
            </Card>

            {/* Heat Index */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">Heat Index</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {Math.round(weatherData.heatIndex)}°F
                  </p>
                  <p className="text-xs text-text-muted">Feels like</p>
                </div>
                <div className="relative">
                  <Sun className="h-8 w-8 text-yellow-400 animate-spin" style={{animationDuration: '8s'}} />
                </div>
              </div>
            </Card>

            {/* Next 6-Hour Peak */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">6-Hour Peak Forecast</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {Math.round(weatherData.nextPeak)}°F
                  </p>
                  <p className="text-xs text-text-muted">Expected at 3:00 PM</p>
                </div>
                <div className="relative">
                  <Cloud className="h-8 w-8 text-gray-400 animate-bounce" />
                </div>
              </div>
            </Card>

            {/* NWS Warning Status */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">NWS Status</p>
                  <p className="text-xl font-bold text-yellow-400">
                    {weatherData.nwsWarning}
                  </p>
                  <p className="text-xs text-text-muted">Active until 8:00 PM</p>
                </div>
                <div className="relative">
                  <AlertTriangle className="h-8 w-8 text-yellow-400 animate-pulse" />
                </div>
              </div>
            </Card>
          </div>

          {/* Grid Metrics */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-heading text-text-primary mb-4">
              ERCOT Grid Status
            </h2>
            
            {/* Real-time Demand */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">Real-time Demand</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {Math.round(gridData.demand).toLocaleString()} MW
                  </p>
                </div>
                <div className="relative">
                  <Zap className="h-8 w-8 text-blue-400" style={{
                    animation: 'pulse 1s ease-in-out infinite alternate'
                  }} />
                </div>
              </div>
            </Card>

            {/* Operating Reserve Margin */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">Reserve Margin</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {Math.round(gridData.reserveMargin).toLocaleString()} MW
                  </p>
                  <p className="text-xs text-text-muted">Safety cushion</p>
                </div>
                <div className="relative">
                  <div className="h-8 w-8 border-2 border-green-400 rounded-full flex items-center justify-center">
                    <div className="h-4 w-4 bg-green-400 rounded-full animate-ping"></div>
                  </div>
                </div>
              </div>
            </Card>

            {/* System-wide Price */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">System Price</p>
                  <p className="text-3xl font-bold text-text-primary">
                    ${Math.round(gridData.price)}/MWh
                  </p>
                </div>
                <div className="relative">
                  <DollarSign className="h-8 w-8 text-green-400 animate-bounce" />
                </div>
              </div>
            </Card>

            {/* Grid Status */}
            <Card variant="elevated">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted mb-1">Grid Status</p>
                  <p className="text-xl font-bold text-green-400">
                    {gridData.status}
                  </p>
                  <p className="text-xs text-text-muted">All systems operational</p>
                </div>
                <div className="relative">
                  <Wind className="h-8 w-8 text-green-400" style={{
                    animation: 'spin 3s linear infinite'
                  }} />
                </div>
              </div>
            </Card>
          </div>

          {/* News Feed */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-heading text-text-primary mb-4">
              Live News Feed
            </h2>
            
            <div className="space-y-4">
              {newsItems.map((item) => (
                <Card key={item.id} variant="paper" className="relative">
                  <div className="flex items-start gap-3">
                    <Newspaper className="h-5 w-5 text-silver-300 mt-1 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-xs font-bold ${getUrgencyColor(item.urgency)}`}>
                          {getUrgencyLabel(item.urgency)}
                        </span>
                        <span className="text-xs text-text-muted">
                          {item.timestamp}
                        </span>
                      </div>
                      <p className="text-sm text-text-primary mb-2 leading-relaxed">
                        {item.title}
                      </p>
                      <p className="text-xs text-text-muted">
                        Source: {item.source}
                      </p>
                    </div>
                  </div>
                  <div className="absolute top-2 right-2 w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                </Card>
              ))}
            </div>

            {/* Query Status */}
            <Card variant="paper">
              <div className="text-center">
                <div className="inline-flex items-center gap-2 text-text-muted">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-xs">Next query in 4:32</span>
                </div>
                <p className="text-xs text-text-muted mt-1">
                  Searching: "Austin Texas ERCOT grid emergency today"
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
