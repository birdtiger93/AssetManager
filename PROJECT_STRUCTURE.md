# AssetManager Project Structure

```
AssetManager/
├── frontend/                 # React Frontend Application
│   ├── src/
│   │   ├── components/      # Reusable React components (TO BE CREATED)
│   │   ├── pages/           # Page components (TO BE CREATED)
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── public/
│   └── package.json
│
├── src/                     # Python Backend Application
│   ├── api/                 # External API integrations (KIS, etc.)
│   ├── auth/                # Authentication & token management
│   ├── database/            # Database models and utilities
│   ├── logic/               # Business logic (trading strategies, calculators)
│   ├── notification/        # Notification services (Telegram, etc.)
│   ├── web/                 # FastAPI web server
│   │   ├── routers/         # API route handlers
│   │   └── app.py           # FastAPI app initialization
│   ├── config_loader.py     # Configuration management
│   ├── scheduler.py         # Background task scheduler
│   └── setup_db.py          # Database initialization
│
├── config/                  # Configuration files
│   └── secrets.yaml         # API keys and secrets (gitignored)
│
├── utils/                   # Utility scripts
│   ├── migrations/          # Database migration scripts
│   ├── debug/               # Debugging and analysis tools
│   └── README.md
│
├── scripts/                 # Development scripts
│   ├── db_shell.py          # Database shell
│   └── test_dashboard.py    # Testing utilities
│
├── docs/                    # Documentation (gitignored)
│   └── API references, etc.
│
├── data/                    # Data files
├── docker-compose.yml       # Docker configuration
├── Dockerfile               # Docker image definition
└── requirements.txt         # Python dependencies
```

## Current Issues & Recommendations

### 1. Frontend Structure (Needs Reorganization)
**Current**: All components in `frontend/src/` root
```
frontend/src/
├── App.jsx
├── Dashboard.jsx
├── Assets.jsx
├── Trade.jsx
├── ProfitLossPage.jsx
├── PeriodReturnsChart.jsx
└── ...
```

**Recommended**: Organize by feature/type
```
frontend/src/
├── components/
│   ├── common/              # Shared components
│   │   ├── Navbar.jsx
│   │   └── Card.jsx
│   └── charts/              # Chart components
│       └── PeriodReturnsChart.jsx
├── pages/                   # Page-level components
│   ├── Dashboard.jsx
│   ├── AssetsPage.jsx
│   ├── TradePage.jsx
│   └── ProfitLossPage.jsx
├── App.jsx
└── main.jsx
```

### 2. Backend Structure (Good, minor improvements)
**Current structure is solid**. Consider:
- Adding `src/services/` for business logic services
- Moving `logic/` contents to `services/`

### 3. Scripts vs Utils
- `scripts/` - Development/testing tools
- `utils/` - One-time maintenance scripts
- Consider merging or clarifying distinction

## Next Steps
1. Reorganize frontend components
2. Clarify scripts vs utils usage
3. Add proper documentation in each directory
