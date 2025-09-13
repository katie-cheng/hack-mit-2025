'use client';

import { useState } from 'react';
import { Home, Phone, CheckCircle, Sparkles, Zap, Star } from 'lucide-react';
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

      const result = await response.json();

      if (response.ok && result.success) {
        setSuccess(true);
        setSuccessData({
          homeownerId: result.homeowner_id
        });
        setFormData({
          name: '',
          phoneNumber: '',
        });
      } else {
        throw new Error(result.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Error registering homeowner:', error);
      setErrors({ submit: error instanceof Error ? error.message : 'Registration failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (field: keyof HomeownerRegistration, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    
    // Clear errors when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: '',
      }));
    }
    if (errors.submit) {
      setErrors(prev => ({
        ...prev,
        submit: '',
      }));
    }
  };

  if (success && successData) {
    return (
      <div className="min-h-screen relative overflow-hidden flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-green-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>

        <Card className="max-w-md w-full text-center rainbow-border pulse-glow relative z-10">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <CheckCircle className="h-16 w-16 text-green-600" />
              <Sparkles className="h-8 w-8 text-yellow-400 absolute -top-2 -right-2 animate-bounce" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Home Registered Successfully! ✨
          </h2>
          <p className="text-gray-600 mb-6">
            Your home is now connected to AURA's smart home management system. 
            You'll receive intelligent weather alerts and automated protection.
          </p>
          
          {/* Registration Confirmation */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-center mb-2">
              <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
              <span className="text-sm font-medium text-gray-700">Registration Complete</span>
            </div>
            <div className="bg-white rounded border-2 border-dashed border-gray-300 p-4">
              <div className="text-sm text-gray-600">
                <p><strong>Homeowner ID:</strong> {successData.homeownerId}</p>
                <p className="mt-2">You're now ready to receive AURA weather alerts!</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <Button
              onClick={() => setSuccess(false)}
              variant="primary"
              className="w-full"
            >
              <Star className="h-4 w-4 mr-2" />
              Register Another Home
            </Button>
            <Button
              onClick={() => window.location.href = '/dashboard'}
              variant="secondary"
              className="w-full"
            >
              <Zap className="h-4 w-4 mr-2" />
              View EOC Dashboard
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden py-8">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="relative inline-block">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 floating">
              Register Your Home
            </h1>
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-lg blur opacity-30"></div>
          </div>
          <p className="text-xl text-white/90 mb-4">
            Connect your home to AURA's intelligent weather protection system
          </p>
        </div>

        <Card className="rainbow-border">
          <form onSubmit={handleSubmit} className="space-y-6 mx-4 my-4">
            {/* Error Display */}
            {errors.submit && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="h-5 w-5 text-red-600">⚠️</div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-800">Registration Error</p>
                    <p className="text-sm text-red-700 mt-1">{errors.submit}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <div className="relative">
                  <Home className="h-5 w-5 mr-2 text-blue-600" />
                  <Sparkles className="h-3 w-3 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
                </div>
                Homeowner Information
              </h3>
              
              <Input
                label="Your Name"
                placeholder="Enter your full name"
                value={formData.name}
                onChange={(e) => updateFormData('name', e.target.value)}
                error={errors.name}
                required
              />

              <Input
                label="Phone Number"
                placeholder="+1 (555) 123-4567"
                value={formData.phoneNumber}
                onChange={(e) => updateFormData('phoneNumber', e.target.value)}
                error={errors.phoneNumber}
                required
                helperText="This is how AURA will contact you for weather alerts"
              />
            </div>

            {/* Privacy Notice */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <div className="relative">
                    <div className="h-6 w-6 text-blue-500">🏠</div>
                    <Sparkles className="h-4 w-4 text-purple-400 absolute -top-1 -right-1 animate-pulse" />
                  </div>
                </div>
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-blue-800">
                    Smart Home Protection ✨
                  </h4>
                  <p className="text-sm text-blue-700 mt-1">
                    AURA will monitor weather conditions and proactively protect your home. 
                    Your information is secure and will only be used for home protection services.
                  </p>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={loading}
                disabled={!formData.name.trim() || !formData.phoneNumber.trim()}
                className="pulse-glow"
              >
                <Home className="h-4 w-4 mr-2" />
                <Sparkles className="h-4 w-4 mr-2" />
                Register Home
              </Button>
            </div>
          </form>
        </Card>

        {/* Additional Information */}
        <Card className="mt-6 rainbow-border">
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <div className="relative">
              <Zap className="h-5 w-5 mr-2 text-indigo-600" />
              <Sparkles className="h-3 w-3 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
            </div>
            How AURA Works
          </h3>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                1
              </div>
              <p>Register your home with basic contact information.</p>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-pink-500 to-red-500 text-white rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                2
              </div>
              <p>Receive intelligent weather alerts via phone call when events are detected.</p>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                3
              </div>
              <p>Get automated home protection including pre-cooling, battery charging, and energy trading.</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
