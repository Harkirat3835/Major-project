# Project Structure

## Directory Organization

```
Major Project/
├── app/                          # Flask backend application
│   ├── __init__.py              # Flask app initialization
│   ├── config.py                # Configuration settings
│   ├── models.py                # Database models (User, Analysis)
│   ├── routes.py                # API endpoints and routes
│   ├── ml_model.py              # Machine learning model for fake news detection
│   └── utils.py                 # Utility functions and helpers
│
├── frontend/                     # React frontend application
│   ├── src/                     # React source code
│   │   ├── components/          # Reusable React components
│   │   ├── pages/               # Page components
│   │   ├── contexts/            # React contexts (Auth, etc)
│   │   ├── lib/                 # Library utilities and API helpers
│   │   ├── App.tsx              # Main App component
│   │   └── main.tsx             # Entry point
│   ├── dist/                    # Built React app (generated)
│   ├── public/                  # Public static assets
│   ├── package.json             # Node dependencies
│   ├── vite.config.ts           # Vite build configuration
│   └── tsconfig.json            # TypeScript configuration
│
├── data/                         # Data files and datasets
│   ├── login_credentials.json   # Demo user credentials
│   ├── user_credentials.json    # User data
│   ├── sample_news.json         # Sample news articles
│   ├── feedback.json            # User feedback data
│   ├── Fake.csv                 # Fake news dataset
│   ├── True.csv                 # Real news dataset
│   └── *.json                   # Other data files
│
├── model/                        # Machine learning models
│   ├── model.pkl                # Trained fake news detection model
│   └── vectorizer.pkl           # Feature vectorizer
│
├── logs/                         # Application logs
│   └── app.log                  # Main application log file
│
├── tests/                        # Test files
│   ├── test_app.py              # Application tests
│   └── __pycache__/             # Python cache
│
├── .venv/                        # Python virtual environment (excluded from commits)
├── .git/                         # Git repository
├── .gitignore                    # Git ignore rules
├── start.ps1                     # Main project launcher (Windows)
├── run.py                        # Flask app entry point
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation

```

## Key Files

### Backend
- `run.py` - Entry point for Flask application
- `requirements.txt` - Python package dependencies
- `app/config.py` - Application configuration

### Frontend
- `frontend/package.json` - Frontend dependencies
- `frontend/vite.config.ts` - Frontend build configuration
- `frontend/dist/` - Compiled React app (served by Flask)

### Launcher
- `start.ps1` - Complete startup script (handles setup, build, and run)

## Running the Project

Simply run:
```powershell
.\start.ps1
```

This script will:
1. Setup Python virtual environment
2. Install all dependencies
3. Build the React frontend
4. Start the Flask server
5. Display startup information and credentials

## Development

### Adding Python Dependencies
Update `requirements.txt` and the script will install them on next run.

### Adding Node Dependencies
Update `frontend/package.json` and the script will install them on next build.

### Accessing the Application
- Main App: http://localhost:5000
- API Docs: http://localhost:5000/api/
- Health Check: http://localhost:5000/api/health

## Demo Credentials

- Username: `admin`, Password: `Admin@1234`
- Username: `inspector`, Password: `Inspect2026!`
- Username: `newsreader`, Password: `ReadNews!23`
