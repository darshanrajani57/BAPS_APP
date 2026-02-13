# BAPS Attendance System - React Frontend

A modern, beautiful React UI for the BAPS Attendance System built with Vite, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Modern UI Design** - Clean, professional interface with smooth animations
- 📱 **Responsive** - Works perfectly on desktop, tablet, and mobile devices
- ⚡ **Fast Performance** - Built with Vite for lightning-fast development and builds
- 🔍 **Search & Filter** - Easy member and session search functionality
- 📊 **Dashboard** - Overview statistics and quick actions
- ✅ **Attendance Tracking** - Easy-to-use attendance marking interface
- 🎯 **Type-Safe** - Full TypeScript support

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites

- Node.js 18+ (20+ recommended)
- npm or yarn
- Flask backend running on `http://localhost:5000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure API URL (optional):
   - The default API URL is `http://localhost:5000/api`
   - To change it, edit `.env` file:
   ```
   VITE_API_URL=http://your-backend-url/api
   ```

3. Start development server:
```bash
npm run dev
```

4. Open your browser:
   - The app will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The production build will be in the `dist` folder.

## Project Structure

```
src/
├── components/       # Reusable UI components
│   └── Layout.tsx   # Main layout with sidebar
├── pages/           # Page components
│   ├── Dashboard.tsx
│   ├── Members.tsx
│   ├── Sessions.tsx
│   ├── CreateSession.tsx
│   ├── SessionAttendance.tsx
│   └── Sevas.tsx
├── lib/             # Utilities and API client
│   └── api/
│       └── client.ts
├── types/           # TypeScript type definitions
│   └── index.ts
├── App.tsx          # Main app component with routing
├── main.tsx         # Entry point
└── index.css        # Global styles (Tailwind)
```

## Pages

### Dashboard
- Overview statistics (members, sessions, sevas)
- Quick action buttons
- Beautiful stat cards

### Members
- View all members in a table
- Search by name, phone, or address
- Filter by role
- Edit member details

### Sessions
- View all sessions (active and ended)
- Create new sessions
- Navigate to attendance marking

### Session Attendance
- Mark attendance for members
- Real-time present/absent counts
- Search members
- Save and end sessions

### Sevas
- View all sevas
- Create new sevas
- Edit and delete sevas

## API Integration

The app connects to the Flask backend REST API. Make sure your backend is running and accessible at the configured API URL.

### API Endpoints Used

- `GET /api/members` - Get all members
- `GET /api/members/:id` - Get member by ID
- `GET /api/sessions` - Get all sessions
- `POST /api/sessions` - Create session
- `GET /api/sessions/:id` - Get session details
- `PUT /api/sessions/:id/end` - End session
- `GET /api/sessions/:id/attendance` - Get attendance
- `POST /api/sessions/:id/attendance` - Update attendance
- `GET /api/sevas` - Get all sevas
- `POST /api/sevas` - Create seva
- `DELETE /api/sevas/:id` - Delete seva

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## UI/UX Features

- **Sidebar Navigation** - Collapsible sidebar with icons
- **Responsive Design** - Mobile-friendly layout
- **Loading States** - Spinner animations during data loading
- **Error Handling** - User-friendly error messages
- **Smooth Animations** - Hover effects and transitions
- **Color-Coded Status** - Visual indicators for session status
- **Search Functionality** - Real-time search filtering
- **Form Validation** - Required field validation

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT
