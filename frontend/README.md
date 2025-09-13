# Aegis Frontend

A Next.js frontend for the Aegis AI-mediated Event Safety Platform. This frontend provides both admin and user interfaces for event safety management.

## Features

### Admin Dashboard (`/admin`)
- Send alerts via text message or voice call
- Choose priority levels (info, warning, emergency)
- Target specific audiences (all attendees, medical conditions, age groups, location-based, custom)
- Real-time alert preview
- Clean, intuitive interface for event organizers

### User Registration (`/user`)
- Simple registration form with phone number and name
- Optional medical information and emergency contacts
- ID verification upload
- Privacy-focused design
- Success confirmation flow

### Home Page (`/`)
- Landing page with feature overview
- Navigation to admin and user sections
- Clear value proposition

## Tech Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Modular component architecture** for easy backend integration

## Getting Started

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── admin/             # Admin dashboard
│   ├── user/              # User registration
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/
│   └── ui/                # Reusable UI components
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── FileUpload.tsx
│       ├── Input.tsx
│       ├── Select.tsx
│       └── Textarea.tsx
├── types/
│   └── api.ts             # TypeScript interfaces for backend integration
└── ...config files
```

## Backend Integration

The frontend is designed for easy backend integration with clear API interfaces:

### User Registration API
```typescript
POST /api/users/register
Content-Type: multipart/form-data

{
  phoneNumber: string;
  name: string;
  medicalInfo?: string;
  emergencyContact?: string;
  age?: number;
  idScan?: File;
}
```

### Alert Sending API
```typescript
POST /api/alerts
Content-Type: application/json

{
  message: string;
  priority: 'info' | 'warning' | 'emergency';
  method: 'text' | 'call';
  target: {
    type: 'all' | 'medical_condition' | 'age_group' | 'location' | 'custom';
    value?: string;
    conditions?: string[];
    ageRange?: { min: number; max: number };
    location?: { latitude: number; longitude: number; radius: number };
  };
}
```

## Component Design

All components are built with:
- **TypeScript interfaces** for props
- **Consistent styling** with Tailwind CSS
- **Accessibility** considerations
- **Error handling** and validation
- **Loading states** for better UX
- **Modular architecture** for easy maintenance

## Customization

### Styling
- Colors and themes can be customized in `tailwind.config.js`
- Component styles are in `app/globals.css`
- Each component uses consistent design tokens

### API Endpoints
- Update API endpoints in the form submission handlers
- Modify request/response types in `types/api.ts`
- Add new form fields by extending the TypeScript interfaces

## Deployment

This frontend is ready for deployment on Vercel:

1. **Connect to Vercel:**
   ```bash
   vercel --prod
   ```

2. **Environment Variables:**
   Set up any required environment variables in your Vercel dashboard

3. **Build:**
   The project will automatically build and deploy

## Integration Notes

- All forms include proper validation and error handling
- File uploads are handled with FormData for backend compatibility
- API calls are structured for easy backend integration
- Components are modular and can be easily extended
- TypeScript interfaces ensure type safety across the application

The frontend is designed to be a clean, professional interface that your backend team can easily integrate with their APIs.
