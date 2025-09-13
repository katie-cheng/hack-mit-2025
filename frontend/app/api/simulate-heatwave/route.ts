import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://127.0.0.1:8000';

export async function POST(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/simulate-heatwave`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to simulate heatwave');
    }

    const result = await response.json();
    
    // Return in expected frontend format
    return NextResponse.json({
      success: result.success,
      message: result.message,
      call_initiated: result.call_initiated,
      call_id: result.call_id,
    });

  } catch (error) {
    console.error('Heatwave simulation error:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to simulate heatwave' 
      },
      { status: 500 }
    );
  }
}
