import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://127.0.0.1:8000';

export async function POST(request: NextRequest) {
  try {
    const registrationData = await request.json();
    
    // Map frontend field names to backend field names
    const backendData = {
      name: registrationData.name,
      phone_number: registrationData.phoneNumber
    };
    
    // Call backend registration API
    const response = await fetch(`${BACKEND_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Backend error:', errorData);
      throw new Error(errorData.detail || errorData.message || 'Registration failed');
    }

    const result = await response.json();
    
    // Return in expected frontend format
    return NextResponse.json({
      success: result.success,
      homeowner_id: result.homeowner_id,
      message: result.message,
    });

  } catch (error) {
    console.error('Registration error:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: error instanceof Error ? error.message : 'Registration failed' 
      },
      { status: 500 }
    );
  }
}
