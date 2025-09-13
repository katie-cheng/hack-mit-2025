'use client';

import { useState, useEffect } from 'react';
import { BarChart3, Thermometer, Battery, DollarSign, Play, RotateCcw, Sparkles, Zap } from 'lucide-react';
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

  useEffect(() => {
    fetchDashboardData();
    // Set up real-time updates - faster during simulation
    const interval = setInterval(fetchDashboardData, simulating ? 500 : 2000);
    return () => clearInterval(interval);
  }, [simulating]);

  const fetchDashboardData = async () => {
    try {
      const [statusResponse, homeownersResponse] = await Promise.all([
        fetch('/api/home-status'),
        fetch('/api/homeowners')
      ]);

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setHomeStatus(statusData.status);
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

  const simulateHeatwave = async () => {
    setSimulating(true);
    setError(null);
    try {
      const response = await fetch('/api/simulate-heatwave', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.message || 'Failed to simulate heatwave');
      }

      console.log('Heatwave simulation initiated:', result);
      
      // Keep simulating state active for the duration of the simulation
      // The simulation typically takes 10-15 seconds
      setTimeout(() => {
        setSimulating(false);
      }, 15000);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to simulate heatwave');
      setSimulating(false);
    }
  };

  const resetSimulation = async () => {
    try {
      const response = await fetch('/api/simulation/reset', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to reset simulation');
      }

      // Refresh data
      await fetchDashboardData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset simulation');
    }
  };

  const getMarketStatusColor = (status: string) => {
    switch (status) {
      case 'monitoring': return 'text-blue-600';
      case 'executing_sale': return 'text-yellow-600';
      case 'success': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getMarketStatusText = (status: string) => {
    switch (status) {
      case 'monitoring': return 'Monitoring';
      case 'executing_sale': return 'Executing Sale';
      case 'success': return 'SUCCESS';
      default: return 'Idle';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen relative overflow-hidden flex items-center justify-center">
        <Card className="p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AURA Dashboard...</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden py-8">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="relative inline-block">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 floating">
              AURA EOC Dashboard
            </h1>
            <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 rounded-lg blur opacity-30"></div>
          </div>
          <p className="text-xl text-white/90">
            Emergency Operations Center - Smart Home Management
          </p>
          
          {/* Simulation Status */}
          {simulating && (
            <div className="mt-4 inline-flex items-center px-4 py-2 bg-yellow-500/20 border border-yellow-400/30 rounded-full">
              <Sparkles className="h-4 w-4 text-yellow-400 animate-spin mr-2" />
              <span className="text-yellow-200 font-medium">Heatwave Response Active</span>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <div className="p-4 text-center text-red-600">
              <p className="font-medium">Error: {error}</p>
            </div>
          </Card>
        )}

        {/* Control Panel */}
        <Card className="mb-8 rainbow-border">
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="h-6 w-6 mr-2 text-purple-600" />
              Control Panel
            </h2>
            <div className="flex flex-wrap gap-4">
              <Button
                onClick={simulateHeatwave}
                disabled={simulating || homeowners.length === 0}
                variant="primary"
                size="lg"
                className="pulse-glow"
              >
                <Play className="h-4 w-4 mr-2" />
                {simulating ? 'Simulating...' : 'Simulate Heatwave'}
              </Button>
              <Button
                onClick={resetSimulation}
                variant="secondary"
                size="lg"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset Simulation
              </Button>
            </div>
            {homeowners.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">
                Register a homeowner first to test the simulation
              </p>
            )}
          </div>
        </Card>

        {/* Smart Home Status Widgets */}
        {homeStatus && (
          <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 ${simulating ? 'animate-pulse' : ''}`}>
            {/* Battery Widget */}
            <Card className="rainbow-border">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Battery className="h-5 w-5 mr-2 text-green-600" />
                    Battery
                  </h3>
                  {homeStatus.solar_charging && (
                    <Sparkles className="h-4 w-4 text-yellow-400 animate-pulse" />
                  )}
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-gray-900 mb-2">
                    {homeStatus.battery_level.toFixed(0)}%
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                    <div 
                      className="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${homeStatus.battery_level}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600">
                    {homeStatus.solar_charging ? 'Charging' : 'Standby'}
                  </p>
                </div>
              </div>
            </Card>

            {/* Thermostat Widget */}
            <Card className="rainbow-border">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Thermometer className="h-5 w-5 mr-2 text-blue-600" />
                    Thermostat
                  </h3>
                  {homeStatus.ac_running && (
                    <Zap className="h-4 w-4 text-blue-400 animate-pulse" />
                  )}
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-gray-900 mb-2">
                    {homeStatus.thermostat_temp.toFixed(0)}°F
                  </div>
                  <p className="text-sm text-gray-600">
                    {homeStatus.ac_running ? 'AC Running' : 'Standby'}
                  </p>
                </div>
              </div>
            </Card>

            {/* Market Widget */}
            <Card className="rainbow-border">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <DollarSign className="h-5 w-5 mr-2 text-orange-600" />
                    Market
                  </h3>
                </div>
                <div className="text-center">
                  <div className={`text-lg font-semibold mb-2 ${getMarketStatusColor(homeStatus.market_status)}`}>
                    {getMarketStatusText(homeStatus.market_status)}
                  </div>
                  {homeStatus.market_status === 'success' && (
                    <div className="text-sm text-gray-600">
                      <p>Sold: {homeStatus.energy_sold} kWh</p>
                      <p>Profit: ${homeStatus.profit_generated.toFixed(2)}</p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Registered Homeowners */}
        <Card className="rainbow-border">
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <div className="relative">
                <div className="h-6 w-6 mr-2 text-indigo-600">🏠</div>
                <Sparkles className="h-4 w-4 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
              </div>
              Registered Homeowners
            </h2>
            
            {homeowners.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🏠</div>
                <p className="text-xl font-semibold text-gray-600">No Homes Registered</p>
                <p className="text-gray-500">Register a home to start monitoring and testing</p>
              </div>
            ) : (
              <div className="space-y-4">
                {homeowners.map((homeowner) => (
                  <div
                    key={homeowner.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-white"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {homeowner.name}
                        </h3>
                        <p className="text-sm text-gray-600">{homeowner.phone_number}</p>
                        <p className="text-xs text-gray-500">
                          Registered: {new Date(homeowner.registered_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-mono font-bold text-gray-800 bg-gray-100 px-3 py-1 rounded">
                          {homeowner.id.slice(0, 8)}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">ID</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
