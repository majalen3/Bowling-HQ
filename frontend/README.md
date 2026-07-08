# Frontend

The frontend service provides the React and Vite user interface for Bowling-HQ.

## Structure

```text
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── types/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── .env.example
└── Dockerfile
```

## Local development

```bash
cp frontend/.env.example frontend/.env
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd frontend
npm test
```
