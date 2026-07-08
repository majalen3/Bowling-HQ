# Frontend Directory

This directory contains all React/TypeScript code for the Bowling-HQ web application.

## Structure

```
frontend/
├── src/
│   ├── main.tsx           → Application entry point
│   ├── App.tsx            → Root component
│   ├── pages/             → Page components
│   │   ├── Home.tsx
│   │   ├── Commander.tsx
│   │   ├── Arsenal.tsx
│   │   ├── Patterns.tsx
│   │   ├── GhostBowler.tsx
│   │   ├── Sessions.tsx
│   │   ├── TournamentBag.tsx
│   │   └── Galaxy.tsx
│   ├── components/        → Reusable components
│   │   ├── RecommendationCard.tsx
│   │   ├── BallSelector.tsx
│   │   ├── ConfidenceDisplay.tsx
│   │   └── ReasoningPanel.tsx
│   ├── services/          → API client
│   │   └── api.ts
│   ├── hooks/             → Custom React hooks
│   │   ├── useRecommendation.ts
│   │   └── useSession.ts
│   ├── types/             → TypeScript types
│   │   ├── ball.ts
│   │   ├── recommendation.ts
│   │   └── session.ts
│   ├── styles/            → Tailwind CSS
│   │   └── globals.css
│   └── utils/             → Helper functions
│       └── formatting.ts
├── public/                → Static assets
├── index.html
├── package.json
├── vite.config.ts        → Vite build config
├── tsconfig.json         → TypeScript config
└── .env.example          → Environment variables
```

## Getting Started

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Run development server
npm run dev

# Build for production
npm run build
```

## Tech Stack

- **Framework**: React 18+
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios

## Development

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.