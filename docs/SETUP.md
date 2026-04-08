# Setup & Installation Guide

## Prerequisites

- Windows 10/11 with PowerShell 5.1+
- Python 3.8+
- Node.js 16+
- Git

## Quick Start

### 1. Navigate to Project Directory
```powershell
cd "C:\Users\YourUsername\OneDrive\Desktop\Major Project"
```

### 2. Run the Startup Script
```powershell
.\start.ps1
```

This will automatically:
- Create Python virtual environment
- Install all Python dependencies
- Install Node.js dependencies
- Build React frontend
- Start Flask server

## Manual Setup (if needed)

### Step 1: Create Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Build Frontend
```powershell
cd frontend
npm install
npm run build
cd ..
```

### Step 4: Run Flask Server
```powershell
python run.py
```

## Accessing the Application

Once started, the application will be available at:
- **Main App**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/
- **Health**: http://localhost:5000/api/health

## Demo Credentials

```
Username: admin
Password: Admin@1234

Username: inspector
Password: Inspect2026!

Username: newsreader
Password: ReadNews!23
```

## Troubleshooting

### PowerShell Execution Policy Error

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found

Ensure Python is installed and in PATH:
```powershell
python --version
```

### Port Already in Use

If port 5000 is in use, modify `run.py`:
```python
port = int(os.environ.get('PORT', 5001))  # Change 5000 to 5001
```

### Dependencies Installation Fails

```powershell
# Clear pip cache
pip cache purge

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```
