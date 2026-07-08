# Quick Start Guide

Get Bowling-HQ running in 5 minutes.

## Prerequisites

- Python 3.11+ or Node.js 18+
- Docker & Docker Compose (optional but recommended)
- Git

## Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/majalen3/Bowling-HQ.git
cd Bowling-HQ

# Start all services
docker-compose up

# Done! 
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/majalen3/Bowling-HQ.git
cd Bowling-HQ

# Setup environment
make setup

# Run development servers
make dev
```

## Next Steps

1. **Read the documentation**: [Full Index](INDEX.md)
2. **Understand the architecture**: [System Architecture](13_ARCHITECTURE.md)
3. **Start coding**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Common Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make test          # Run all tests
make lint          # Run code quality checks
make clean         # Clean generated files
```

## Troubleshooting

**Port already in use?**
```bash
# Change ports in .env file
VITE_PORT=5174
API_PORT=8001
```

**Database connection error?**
```bash
# Make sure Docker is running
docker-compose ps

# Restart services
docker-compose restart
```

## Need Help?

- Check [Full Documentation](INDEX.md)
- Review [Contributing Guide](../CONTRIBUTING.md)
- Check commit history for examples

---

**Ready to dive deeper?** Start with [Project Overview](01_PROJECT_OVERVIEW.md).
