# ID Processing Integration

## Overview
The ID processing functionality has been integrated into the frontend user registration form. When a user uploads an ID image, it will automatically extract and fill in the following form fields:

- **Name** (from first_name + last_name)
- **Age** (calculated from birthday)
- **Gender** (extracted from ID)

## Setup Required

### 1. Environment Variable
You need to set the XAI_API_KEY environment variable for the ID processing to work:

```bash
# In your terminal
export XAI_API_KEY="your_xai_api_key_here"

# Or create a .env.local file in the frontend directory
echo "XAI_API_KEY=your_xai_api_key_here" > frontend/.env.local
```

### 2. Python Dependencies
Make sure the Python dependencies are installed:

```bash
pip install -r requirements.txt
```

## How It Works

1. User uploads an ID image using the file upload component
2. Frontend sends the image to `/api/process-id` endpoint
3. API route calls the Python `process.py` script with the image
4. Python script uses Grok API to extract information
5. Extracted data is returned and automatically fills the form fields
6. User can review and modify the auto-filled data before submitting

## Files Modified

- `frontend/app/api/process-id/route.ts` - New API endpoint for ID processing
- `frontend/types/api.ts` - Added gender field and ID processing response types
- `frontend/app/user/page.tsx` - Integrated ID processing into user registration form

## Error Handling

- If ID processing fails, the form fields remain empty (no error shown to user)
- Processing status is shown with a loading indicator
- All errors are logged to console for debugging

## Testing

To test the integration:

1. Set up the XAI_API_KEY environment variable
2. Start the frontend development server: `npm run dev`
3. Go to the user registration page
4. Upload an ID image
5. Watch the form fields auto-fill with extracted data
