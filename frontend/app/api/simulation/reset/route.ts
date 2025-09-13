import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://127.0.0.1:8000';

export async function POST(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/simulation/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to reset simulation');
    }

    const result = await response.json();
    
    return NextResponse.json({
      success: result.success,
      message: result.message,
    });

  } catch (error) {
    console.error('Simulation reset error:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to reset simulation' 
      },
      { status: 500 }
    );
  }
}
