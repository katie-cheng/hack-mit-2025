'use client';

import { useState } from 'react';
import { Home, Phone, CheckCircle, Zap, Star } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface HomeownerRegistration {
  name: string;
  phoneNumber: string;
}

export default function RegisterPage() {
  const [formData, setFormData] = useState<HomeownerRegistration>({
    name: '',
    phoneNumber: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [successData, setSuccessData] = useState<{ homeownerId: string } | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (!/^\+?[\d\s\-\(\)]+$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = 'Please enter a valid phone number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        setSuccessData(result);
        setSuccess(true);
      } else {
        console.error('Registration failed');
      }
    } catch (error) {
      console.error('Error during registration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof HomeownerRegistration) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  if (success && successData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" data-content="main">
        <Card variant="paper" glow className="max-w-md w-full text-center">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 mb-4 silver-glow border border-silver-400/40" style={{background: 'transparent', borderRadius: '0px'}}>
              <CheckCircle className="h-8 w-8 text-status-success" />
            </div>
            <h2 className="text-2xl font-bold text-display text-text-primary mb-2">
              Registration Successful!
            </h2>
            <p className="text-body text-text-secondary font-light">
              Welcome to Mercury's intelligent energy management system.
            </p>
          </div>
          
          <div className="p-4 mb-6 border border-silver-400/40" style={{background: 'transparent', borderRadius: '0px', boxShadow: '0 0 15px rgba(192, 192, 192, 0.1)'}}>
            <p className="text-sm text-text-muted mb-1">Your Homeowner ID</p>
            <p className="text-mono text-lg font-semibold text-text-primary">
              {successData.homeownerId}
            </p>
          </div>
          
          <div className="space-y-4 mb-6">
            <div className="flex items-center text-left">
              <Zap className="h-5 w-5 text-silver-300 mr-3 flex-shrink-0" />
              <span className="text-body text-text-secondary">
                Your home is now connected to Mercury's energy network
              </span>
            </div>
            <div className="flex items-center text-left">
              <Phone className="h-5 w-5 text-silver-300 mr-3 flex-shrink-0" />
              <span className="text-body text-text-secondary">
                You'll receive voice alerts for critical energy events
              </span>
            </div>
            <div className="flex items-center text-left">
              <Star className="h-5 w-5 text-silver-300 mr-3 flex-shrink-0" />
              <span className="text-body text-text-secondary">
                AI-powered optimization is now active for your home
              </span>
            </div>
          </div>
          
          <div className="flex flex-col gap-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                variant="primary"
                onClick={() => window.location.href = '/dashboard'}
                className="flex-1"
                glow
              >
                View Dashboard
              </Button>
              <Button
                variant="secondary"
                onClick={() => {
                  setSuccess(false);
                  setSuccessData(null);
                  setFormData({ name: '', phoneNumber: '' });
                }}
                className="flex-1"
              >
                Register Another
              </Button>
            </div>
            <Button
              variant="secondary"
              onClick={() => window.location.href = '/weather'}
              className="w-full"
            >
              Go to Threat Assessment
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4" data-content="main">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 pt-8">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 silver-glow border border-silver-400/40" style={{background: 'transparent', borderRadius: '0px'}}>
            <Home className="h-8 w-8 text-silver-200" />
          </div>
          <h1 className="text-4xl font-bold text-display text-text-primary mb-4">
            Register Your Home
          </h1>
          <p className="text-lg text-body text-text-secondary font-light max-w-2xl mx-auto">
            Connect your home to Mercury's intelligent energy management system and unlock the power of automated optimization.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Registration Form */}
          <Card variant="elevated">
            <h2 className="text-2xl font-semibold text-heading text-text-primary mb-6">
              Homeowner Information
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <Input
                label="Full Name"
                type="text"
                value={formData.name}
                onChange={handleInputChange('name')}
                error={errors.name}
                helperText="Enter your full legal name"
                placeholder="John Doe"
                required
              />

              <Input
                label="Phone Number"
                type="tel"
                value={formData.phoneNumber}
                onChange={handleInputChange('phoneNumber')}
                error={errors.phoneNumber}
                helperText="We'll use this for voice alerts and notifications"
                placeholder="+1 (555) 123-4567"
                required
              />

              <div className="p-4 border border-silver-400/40" style={{background: 'transparent', borderRadius: '0px', boxShadow: '0 0 15px rgba(192, 192, 192, 0.1)'}}>
                <div className="flex items-start">
                  <Zap className="h-5 w-5 text-silver-300 mr-3 mt-0.5 flex-shrink-0" />
                  <div className="text-sm">
                    <p className="text-text-primary font-medium mb-1">Privacy Notice</p>
                    <p className="text-text-muted">
                      Your information is encrypted and used solely for energy management and emergency notifications. 
                      Mercury never shares your data with third parties.
                    </p>
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                loading={loading}
                disabled={loading}
                className="w-full"
                glow
              >
                Register Home
              </Button>
            </form>
          </Card>

          {/* How Mercury Works */}
          <div className="space-y-6">
            <Card variant="paper">
              <h3 className="text-xl font-semibold text-heading text-text-primary mb-4">
                How Mercury Works
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center text-sm font-semibold text-text-primary mr-4 border border-silver-400/40" style={{background: 'transparent', borderRadius: '0px', boxShadow: '0 0 10px rgba(192, 192, 192, 0.08)'}}>
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-text-primary mb-1">Smart Monitoring</h4>
                    <p className="text-body text-text-secondary">
                      Mercury continuously monitors grid conditions, weather patterns, and your home's energy usage.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center text-sm font-semibold text-text-primary mr-4 border border-silver-400/40" style={{background: 'transparent', borderRadius: '0px', boxShadow: '0 0 10px rgba(192, 192, 192, 0.08)'}}>
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-text-primary mb-1">Predictive Analysis</h4>
                    <p className="text-body text-text-secondary">
                      AI algorithms predict energy events and automatically prepare your home's systems.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center text-sm font-semibold text-text-primary mr-4 border border-silver-400/40" style={{background: 'transparent', borderRadius: '0px', boxShadow: '0 0 10px rgba(192, 192, 192, 0.08)'}}>
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-text-primary mb-1">Voice Notifications</h4>
                    <p className="text-body text-text-secondary">
                      Receive timely voice calls about critical events and system optimizations.
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            <Card variant="elevated" shimmer>
              <div className="text-center">
                <Zap className="h-12 w-12 text-silver-300 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-heading text-text-primary mb-2">
                  Intelligent Energy Management
                </h4>
                <p className="text-body text-text-secondary">
                  Join thousands of homeowners who have reduced their energy costs by up to 30% with Mercury's AI-powered optimization.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}