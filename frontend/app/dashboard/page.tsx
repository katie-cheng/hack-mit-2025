'use client';

import { useState, useEffect } from 'react';
import { BarChart3, Thermometer, Battery, DollarSign, Play, RotateCcw, Zap, Users } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

interface HomeStatus {
  battery_level: number;
  thermostat_temp: number;
  market_status: 'monitoring' | 'executing_sale' | 'success' | 'idle';
  energy_sold: number;
  profit_generated: number;
  solar_charging: boolean;
  ac_running: boolean;
  last_updated: string;
}

interface Homeowner {
  id: string;
  name: string;
  phone_number: string;
  registered_at: string;
}

export default function DashboardPage() {
  const [homeStatus, setHomeStatus] = useState<HomeStatus | null>(null);
  const [homeowners, setHomeowners] = useState<Homeowner[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      const [statusResponse, homeownersResponse] = await Promise.all([
        fetch('/api/home-status', {
          cache: 'no-store',
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        }),
        fetch('/api/homeowners', {
          cache: 'no-store',
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        })
      ]);

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        console.log('📊 API Response:', statusData.status);
        console.log('🔄 Current state:', homeStatus);
        console.log('🆕 New data equals current?', JSON.stringify(statusData.status) === JSON.stringify(homeStatus));
        setHomeStatus(statusData.status);
        console.log('✅ State updated');
      }

      if (homeownersResponse.ok) {
        const homeownersData = await homeownersResponse.json();
        setHomeowners(homeownersData.homeowners);
      }

      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial data fetch
    fetchDashboardData();
    
    // Set up real-time updates - simple 1 second polling for consistent updates
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 1000);
    
    return () => clearInterval(interval);
  }, []); // Empty dependency array for one-time setup

  const simulateHeatwave = async () => {
    setSimulating(true);
    try {
      const response = await fetch('/api/simulate-heatwave', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        throw new Error('Simulation failed');
      }

      // Simulation will run for about 30 seconds
      setTimeout(() => setSimulating(false), 35000);
    } catch (err) {
      console.error('Simulation error:', err);
      setSimulating(false);
    }
  };

  const resetSimulation = async () => {
    try {
      const response = await fetch('/api/simulation/reset', {
        method: 'POST'
      });

      if (response.ok) {
        fetchDashboardData();
      }
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  const getBatteryStatusColor = (level: number) => {
    if (level >= 80) return 'text-status-success';
    if (level >= 50) return 'text-status-warning';
    return 'text-status-danger';
  };

  const getMarketStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-status-success';
      case 'executing_sale': return 'text-status-warning';
      case 'monitoring': return 'text-status-info';
      default: return 'text-text-muted';
    }
  };

  const getMarketStatusText = (status: string) => {
    switch (status) {
      case 'success': return 'Sale Complete';
      case 'executing_sale': return 'Executing Sale';
      case 'monitoring': return 'Monitoring';
      default: return 'Idle';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-mercury mb-4 mx-auto"></div>
          <p className="text-body text-text-secondary">Loading Mercury dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4" data-content="main">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center mb-2">
              <Zap className="h-8 w-8 text-silver-200 mr-3 silver-glow" />
              <h1 className="text-4xl font-bold text-display text-text-primary">
                Mercury EOC Dashboard
              </h1>
            </div>
            <p className="text-body text-text-secondary">
              Intelligent Energy Operations Center
            </p>
          </div>
        </div>

        {error && (
          <Card variant="elevated" className="mb-6 border-status-danger">
            <div className="flex items-center">
              <Zap className="h-5 w-5 text-status-danger mr-3" />
              <p className="text-body text-status-danger">{error}</p>
            </div>
          </Card>
        )}

        {/* Simulation Controls */}
        <Card variant="paper" className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-heading text-text-primary mb-2">
                Simulation Control Panel
              </h2>
              <p className="text-body text-text-secondary">
                {simulating 
                  ? 'Heatwave simulation in progress - voice calls active' 
                  : 'Ready to simulate emergency heatwave response'}
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                onClick={simulateHeatwave}
                disabled={simulating}
                loading={simulating}
                variant="primary"
                glow
              >
                <Play className="h-4 w-4 mr-2" />
                {simulating ? 'Simulating...' : 'Simulate Heatwave'}
              </Button>
              <Button
                onClick={resetSimulation}
                disabled={simulating}
                variant="secondary"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset
              </Button>
            </div>
          </div>
        </Card>

        {/* Status Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Battery Status */}
          <Card variant="elevated" shimmer>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-heading text-text-primary">Battery</h3>
              <Battery className={`h-6 w-6 ${getBatteryStatusColor(homeStatus?.battery_level || 0)}`} />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-body text-text-secondary">Charge Level</span>
                <span className={`font-semibold ${getBatteryStatusColor(homeStatus?.battery_level || 0)}`}>
                  {homeStatus?.battery_level || 0}%
                </span>
              </div>
              <div className="w-full bg-mercury-600 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-mercury-500 to-silver-400 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${homeStatus?.battery_level || 0}%` }}
                />
              </div>
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-2 ${homeStatus?.solar_charging ? 'bg-status-success animate-pulse' : 'bg-text-muted'}`} />
                <span className="text-sm text-text-muted">
                  {homeStatus?.solar_charging ? 'Solar Charging Active' : 'Solar Standby'}
                </span>
              </div>
            </div>
          </Card>

          {/* Thermostat */}
          <Card variant="elevated" shimmer>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-heading text-text-primary">Thermostat</h3>
              <Thermometer className="h-6 w-6 text-status-info" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-body text-text-secondary">Temperature</span>
                <span className="font-semibold text-text-primary">
                  {homeStatus?.thermostat_temp || 72}°F
                </span>
              </div>
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-2 ${homeStatus?.ac_running ? 'bg-status-info animate-pulse' : 'bg-text-muted'}`} />
                <span className="text-sm text-text-muted">
                  {homeStatus?.ac_running ? 'AC Running' : 'AC Standby'}
                </span>
              </div>
            </div>
          </Card>

          {/* Market Status */}
          <Card variant="elevated" shimmer>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-heading text-text-primary">Market</h3>
              <DollarSign className={`h-6 w-6 ${getMarketStatusColor(homeStatus?.market_status || 'idle')}`} />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-body text-text-secondary">Status</span>
                <span className={`font-semibold ${getMarketStatusColor(homeStatus?.market_status || 'idle')}`}>
                  {getMarketStatusText(homeStatus?.market_status || 'idle')}
                </span>
              </div>
              {(homeStatus?.energy_sold ?? 0) > 0 && (
                <div className="flex justify-between">
                  <span className="text-body text-text-secondary">Energy Sold</span>
                  <span className="font-semibold text-text-primary">
                    {homeStatus?.energy_sold} kWh
                  </span>
                </div>
              )}
              {(homeStatus?.profit_generated ?? 0) > 0 && (
                <div className="flex justify-between">
                  <span className="text-body text-text-secondary">Profit</span>
                  <span className="font-semibold text-status-success">
                    ${homeStatus?.profit_generated?.toFixed(2)}
                  </span>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Registered Homeowners */}
        <Card variant="paper">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-semibold text-heading text-text-primary mb-2">
                Registered Homeowners
              </h2>
              <p className="text-body text-text-secondary">
                Connected homes in the Mercury energy network
              </p>
            </div>
            <div className="flex items-center">
              <Users className="h-5 w-5 text-silver-300 mr-2" />
              <span className="text-lg font-semibold text-text-primary">{homeowners.length}</span>
            </div>
          </div>
          
          {homeowners.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-text-muted mx-auto mb-4" />
              <p className="text-body text-text-muted">No homeowners registered yet</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {homeowners.map((homeowner) => (
                <Card key={homeowner.id} variant="elevated" className="bg-mercury-600">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-text-primary mb-1">{homeowner.name}</h3>
                      <p className="text-sm text-text-muted mb-2">{homeowner.phone_number}</p>
                      <p className="text-xs text-text-muted">
                        ID: {homeowner.id}
                      </p>
                    </div>
                    <div className="w-2 h-2 bg-status-success rounded-full animate-pulse" title="Connected" />
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Card>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-body text-text-muted">
            Last updated: {homeStatus?.last_updated ? new Date(homeStatus.last_updated).toLocaleString() : 'Never'}
          </p>
        </div>
      </div>
    </div>
  );
}