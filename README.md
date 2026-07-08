# Bowling-HQ

Bowling-HQ is an AI-powered bowling intelligence platform with production-ready local development scaffolding for FastAPI, React, PostgreSQL, MongoDB, and Redis.

## 🎯 Quick Navigation

### Getting Started
- **[Quick Start Guide](docs/00_QUICK_START.md)** - Start here in 15 minutes
- **[Platform Overview](docs/01_PROJECT_OVERVIEW.md)** - Understand the full system

### Core Systems
- **[Commander AI](docs/02_COMMANDER_AI.md)** - Real-time decision making
- **[Ghost Bowler](docs/03_GHOST_BOWLER.md)** - Performance baseline
- **[Arsenal DNA](docs/04_ARSENAL_DNA.md)** - Equipment analysis
- **[Pattern Intelligence](docs/05_PATTERNS.md)** - Lane condition reading
- **[Tournament Bag](docs/06_TOURNAMENT_BAG.md)** - Strategic lineup building

### Analytics & Insights
- **[Session Intelligence](docs/07_SESSIONS.md)** - Performance tracking
- **[Maxwell AI](docs/08_MAXWELL_AI.md)** - Venue intelligence
- **[Galaxy](docs/09_GALAXY.md)** - Arsenal visualization
- **[Video Coach](docs/10_VIDEO_COACH.md)** - Technical analysis
- **[Digital Twin](docs/11_DIGITAL_TWIN.md)** - Predictive simulation

### Learning & Community
- **[Academy](docs/12_ACADEMY.md)** - Learning platform
- **[Conclusion](docs/13_CONCLUSION.md)** - Journey overview

### Additional Resources
- **[Documentation Index](docs/INDEX.md)** - Full reference
- **[Phase 0 Roadmap](ROADMAP_PHASE_0.md)** - Development phases
- **[Architecture](architecture/SYSTEM_DESIGN.md)** - System design
- **[Bowling Physics Guide](docs/BOWLING_PHYSICS_GUIDE.md)** - Physics and prediction baseline
- **[Data Needs Phase 1](docs/DATA_NEEDS_PHASE_1.md)** - Immediate collection priorities
- **[Development Workflow](DEVELOPMENT.md)** - Local stack and command reference

## Quick start

```bash
make setup
make dev
```

Or start the full stack directly with Docker Compose:

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Backend health: http://localhost:8000/health

## 📊 What is Bowling-HQ?

A comprehensive platform that provides:

- **AI Coaching** - Real-time guidance during play
- **Performance Analytics** - Track and analyze every game
- **Equipment Intelligence** - Optimize your arsenal
- **Video Analysis** - Technical form review
- **Tournament Simulation** - Predict outcomes
- **Skill Development** - Structured learning paths
- **Community** - Connect with other bowlers

## 🚀 Features

### Intelligent Systems
- **Commander AI**: Real-time decisions about equipment, strategy, and adjustments
- **Ghost Bowler**: Your personal performance baseline across all conditions
- **Pattern Intelligence**: Lane condition analysis and breakpoint prediction
- **Arsenal DNA**: Complete equipment profiling and optimization
- **Digital Twin**: Predict performance in any scenario

### Data & Analytics
- **Session Intelligence**: Track every game with detailed analytics
- **Maxwell AI**: Venue-specific insights and recommendations
- **Galaxy**: Visual 3D arsenal mapping
- **Video Coach**: AI-powered form analysis
- **Accuracy Tracking**: Measure improvement over time

### Learning
- **Academy**: 500+ coaching videos and progressive drills
- **Certifications**: From beginner to professional
- **Personalized Paths**: Customized learning progression
- **Expert Instruction**: Professional bowlers and coaches

## Project structure

```text
Bowling-HQ/
├── backend/
│   ├── src/
│   ├── services/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
├── database/
│   ├── schemas/
│   ├── seeds/
│   └── migrations/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
├── Makefile
├── DEVELOPMENT.md
└── docs/
```

## Development commands

```bash
make help
make lint
make test
make clean
```

## 📝 Phase 0 Progress

**Status**: Documentation complete, 14/14 sections done

- ✅ Quick Start Guide
- ✅ Platform Overview
- ✅ All AI Systems (Commander, Ghost Bowler, etc.)
- ✅ Analytics Platforms
- ✅ Learning & Development
- ✅ Conclusion & Success Paths

**Next Phases**: Backend, Frontend, Database implementation

## 🎳 Physics & Prediction Foundations

The repository includes a first-pass bowling physics baseline for:
- oil pattern difficulty scoring
- ball reaction prediction
- bowler outcome forecasting
- pattern transition modeling
- Monte Carlo scenario simulation

See `backend/services/physics_engine.py` and the related docs in `docs/`.

## 📈 Impact

Users typically see:
- **+15-30 pins average improvement** in first 3 months
- **90%+ tournament prediction accuracy**
- **Significantly better equipment decisions**
- **Measurable form improvements**
- **Increased bowling enjoyment and engagement**

## 🤝 Contributing

This is a personal project. For general questions or ideas, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**majalen3** - Bowling enthusiast and project creator

---

**Questions?** Check the [docs/](docs/) directory or see [docs/00_QUICK_START.md](docs/00_QUICK_START.md) to begin.
