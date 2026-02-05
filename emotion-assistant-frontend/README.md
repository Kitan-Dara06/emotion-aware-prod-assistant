# Emotion-Aware Productivity Assistant - Frontend

A modern, emotion-aware chat interface built with React, Vite, and TypeScript.

## Features

- 🎨 **Beautiful UI**: Glassmorphism design with smooth animations
- 🌈 **28 Emotion Colors**: Visual indicators for all emotions from the go_emotions dataset
- 💬 **Real-time Chat**: Optimistic updates and auto-scroll
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast**: Built with Vite for lightning-fast development and builds

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Vanilla CSS** - Custom styling with design system

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v2
```

## Development

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
src/
├── components/          # React components
│   ├── ChatContainer/   # Main chat interface
│   ├── MessageBubble/   # Individual message display
│   ├── ChatInput/       # Message input area
│   ├── EmotionIndicator/# Emotion visualization
│   ├── Header/          # App header
│   └── TypingIndicator/ # Loading indicator
├── hooks/               # Custom React hooks
│   └── useChat.ts       # Chat state management
├── services/            # API client
│   └── api.ts           # Backend API calls
├── types/               # TypeScript definitions
│   └── api.ts           # API types
├── context/             # React context
│   └── AppContext.tsx   # Global app state
├── styles/              # Global styles
│   └── animations.css   # Animation keyframes
├── index.css            # Design system & utilities
├── App.tsx              # Main app component
└── main.tsx             # Entry point
```

## Design System

The app uses a comprehensive design system with:

- **28 Emotion Colors**: Each emotion has a unique gradient
- **Spacing Scale**: Consistent spacing from xs to 2xl
- **Typography**: Inter for body text, Space Grotesk for headings
- **Glassmorphism**: Backdrop blur effects throughout
- **Smooth Animations**: Entrance animations, micro-interactions, and transitions

## API Integration

The frontend communicates with the backend via REST API:

- `POST /api/v2/chat` - Send message and get response
- `POST /api/v2/history` - Get conversation history
- `DELETE /api/v2/history/:userId` - Clear history
- `GET /api/v2/health` - Health check

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT
