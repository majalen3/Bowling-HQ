# Getting Started - Local Development

## Prerequisites

- Git
- Python 3.10+ (for backend)
- Node.js 18+ (for frontend)
- Docker (optional, recommended)
- PostgreSQL 13+ (or Docker)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/majalen3/Bowling-HQ.git
cd Bowling-HQ
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# See .env.example for required variables
```

### 3. Using Make Commands

```bash
# View all available commands
make help

# Install dependencies (when backend/frontend are implemented)
make install

# Start development environment
make dev

# Run tests (when tests are implemented)
make test

# Build for production
make build

# Start production environment
make start

# Stop running services
make stop

# Clean up
make clean
```

### 4. Using Docker (Optional)

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up

# Stop services
docker-compose down
```

## Project Structure

```
Bowling-HQ/
├── backend/              # Backend API (Python/Node.js)
│   ├── app/             # Main application
│   ├── tests/           # Tests
│   └── requirements.txt # Dependencies
├── frontend/             # Frontend (React)
│   ├── src/             # Source code
│   ├── public/          # Static files
│   └── package.json     # Dependencies
├── database/             # Database
│   ├── migrations/      # Schema migrations
│   └── seeds/           # Seed data
├── docs/                 # Documentation
├── architecture/         # System design
├── Makefile             # Build automation
├── docker-compose.yml   # Docker configuration
└── .env.example         # Environment template
```

## Development Workflow

### Backend Development

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --reload

# Run tests
pytest
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Database Setup

```bash
# Create database
creatdb bowling_hq

# Run migrations
alembic upgrade head

# Seed sample data (optional)
python scripts/seed_data.py
```

## Common Commands

```bash
# Check code style
make lint

# Format code
make format

# Run type checking
make type-check

# Run security checks
make security-check

# View logs
make logs

# Drop and recreate database
make reset-db
```

## Debugging

### Backend Debugging

```bash
# Add to Python code
import pdb; pdb.set_trace()

# Or use debugger in IDE
# VSCode: Create .vscode/launch.json with debugger config
```

### Frontend Debugging

```bash
# Use browser DevTools (F12)
# Use React DevTools Chrome extension
# Use Redux DevTools for state inspection
```

### Database Debugging

```bash
# Connect to database
psql bowling_hq

# View tables
\dt

# Query data
SELECT * FROM users LIMIT 10;
```

## Testing

```bash
# Run all tests
make test

# Run backend tests
make test-backend

# Run frontend tests
make test-frontend

# Run with coverage
make test-coverage

# Run specific test
pytest tests/test_user.py::test_create_user
```

## API Development

API endpoints are documented in `/docs/API.md` (when created).

Common endpoints:
- `POST /api/sessions` - Create session
- `GET /api/sessions/{id}` - Get session
- `POST /api/videos` - Upload video
- `GET /api/analysis/{id}` - Get analysis results

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Reset connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/bowling_hq
```

### Node Module Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Python Dependency Issues

```bash
# Create fresh virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add my feature"

# Push to repository
git push origin feature/my-feature

# Create pull request on GitHub
```

## Documentation

- Platform docs: `/docs/`
- Architecture: `/architecture/SYSTEM_DESIGN.md`
- API reference: `/docs/API.md` (planned)
- Contributing: `/CONTRIBUTING.md`

## Getting Help

- Check existing issues on GitHub
- Review documentation thoroughly
- Open a new issue with details
- See `/SUPPORT.md` for more options

## Next Steps

1. Read [Platform Overview](docs/01_PROJECT_OVERVIEW.md)
2. Explore system documentation in `/docs/`
3. Set up local environment
4. Start building!

---

**Happy coding! 🎳**
