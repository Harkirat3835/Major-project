# Fake News Detection API - Professional Edition

A comprehensive, enterprise-grade fake news detection system built with Flask, featuring AI-powered analysis, user authentication, real-time monitoring, and professional API documentation.

## 🚀 Features

### Core Features
- **AI-Powered Detection**: Advanced machine learning model for fake news classification
- **Real-time Analysis**: Instant prediction with confidence scores and detailed reasoning
- **Professional API**: RESTful API with comprehensive documentation
- **User Authentication**: JWT-based secure authentication system
- **Database Persistence**: PostgreSQL/SQLite support for data storage
- **Analysis History**: Track and review past predictions
- **Feedback System**: User feedback to improve model accuracy

### Enterprise Features
- **Rate Limiting**: API protection with configurable limits
- **Caching**: Redis-powered caching for improved performance
- **Monitoring**: Prometheus metrics for real-time monitoring
- **Background Tasks**: Celery support for async processing
- **Comprehensive Logging**: Structured logging with multiple handlers
- **Health Checks**: Automated health monitoring endpoints

### Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Cross-origin resource sharing enabled
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Graceful error handling with detailed messages
- **Database Migrations**: Flask-Migrate for schema management

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **Authentication**: Flask-JWT-Extended
- **API Documentation**: Flask-RESTX
- **Caching**: Flask-Caching with Redis
- **Rate Limiting**: Flask-Limiter
- **Monitoring**: Prometheus Flask Exporter
- **Async Tasks**: Celery
- **ML Framework**: Scikit-learn (optional, rule-based fallback available)
- **Frontend**: Bootstrap 5 + Vanilla JavaScript

## 📋 Prerequisites

- **Required**: Python 3.8+
- **Optional**: Node.js (for React frontend), Redis (for caching), PostgreSQL (alternative to SQLite)
- **ML Dependencies**: pandas, numpy, scikit-learn (optional - app works with rule-based analysis)

## ⚠️ Important Notes

- **Core functionality works without ML libraries**: The application uses rule-based fake news detection as fallback
- **Optional dependencies**: Install `pandas`, `numpy`, and `scikit-learn` for enhanced ML analysis
- **Database**: Uses SQLite by default, no additional setup required
- **Frontend**: Flask serves HTML templates by default; React frontend is optional

## 🚀 Quick Start

### Quick Start (Recommended)
```powershell
.\start.ps1
```

This unified script handles:
- Python venv + deps
- Frontend npm install + build
- Flask server start

### Manual Backend (Flask)
```bash
python run.py
```
Access: http://localhost:5000

### Manual Frontend Dev
```bash
cd frontend
npm run dev
```
Access: http://localhost:5173

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fake-news-detection
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies (for React frontend)**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Set up environment variables** (optional)
   ```bash
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key
   export DATABASE_URL=sqlite:///app.db
   export REDIS_URL=redis://localhost:6379/0
   ```

6. **Run the applications**

   **Backend (Flask + HTML Templates):**
   ```bash
   python run.py
   ```
   Access at: http://localhost:5000

   **Frontend (React Application):**
   ```bash
   cd frontend
   npm run dev
   ```
   Access at: http://localhost:5173

## 🖥️ Application Interfaces

This project provides two user interfaces:

### 1. Flask Backend with HTML Templates
- **URL**: http://localhost:5000
- **Features**: Complete web application with modern glassmorphism UI
- **Technology**: Flask + Bootstrap 5 + Custom CSS
- **Best for**: Quick deployment, traditional web app experience

### 2. React Frontend Application
- **URL**: http://localhost:5173
- **Features**: Modern React SPA with advanced components
- **Technology**: React + TypeScript + Vite
- **Best for**: Rich user interactions, modern development workflow

Both interfaces connect to the same Flask API backend for analysis functionality.

## 📖 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "johndoe",
    "password": "securepassword"
}
```

### Analysis Endpoints

#### Analyze News (Authenticated)
```http
POST /api/analysis/predict
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
    "text": "Your news article text here..."
}
```

#### Get Analysis History
```http
GET /api/analysis/
Authorization: Bearer <jwt-token>
```

#### Submit Feedback
```http
POST /api/analysis/{analysis_id}/feedback
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
    "is_correct": true,
    "comment": "Optional feedback comment"
}
```

### User Management

#### Get User Profile
```http
GET /api/user/profile
Authorization: Bearer <jwt-token>
```

## 🎯 Usage Examples

### Python Client
```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'testuser',
    'password': 'password'
})
token = response.json()['access_token']

# Analyze news
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:5000/api/analysis/predict',
    headers=headers,
    json={'text': 'Your news article text here...'}
)

print(response.json())
```

### JavaScript Client
```javascript
// Analyze news
const response = await fetch('/api/analysis/predict', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        text: 'Your news article text here...'
    })
});

const result = await response.json();
console.log(result);
```

## 🏗️ Project Structure

```
fake-news-detection/
├── app/
│   ├── __init__.py          # Application factory
│   ├── routes.py            # API routes and views
│   ├── models.py            # Database models
│   ├── config.py            # Configuration management
│   ├── ml_model.py          # ML model and prediction logic
│   └── utils.py             # Utility functions
├── templates/
│   └── index.html           # Web interface
├── data/
│   ├── Fake.csv            # Fake news training data
│   └── True.csv            # Real news training data
├── model/                  # Trained ML models
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md              # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `SECRET_KEY` | `dev-secret` | JWT secret key |
| `DATABASE_URL` | `sqlite:///app.db` | Database connection URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiration |

### Database Configuration

The application supports multiple database backends:

- **SQLite** (default): `sqlite:///app.db`
- **PostgreSQL**: `postgresql://user:password@localhost/dbname`
- **MySQL**: `mysql://user:password@localhost/dbname`

## 🔧 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Formatting
```bash
black app/
flake8 app/
```

### Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📊 Monitoring

### Health Checks
- **Application Health**: `GET /api/health`
- **Metrics**: `GET /metrics` (Prometheus format)

### Key Metrics
- Request count and latency
- Database connection status
- Cache hit/miss ratios
- Model prediction statistics

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

### Production Considerations
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up reverse proxy (Nginx)
- Configure SSL/TLS
- Set secure environment variables
- Enable monitoring and logging
- Set up database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask and modern Python practices
- Inspired by real-world fake news detection challenges
- Uses open-source ML techniques and best practices

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the API documentation
- Review the logs for debugging information

---

**Professional Fake News Detection API v2.0**
*Built for accuracy, security, and scalability*
   python run.py
   ```

   The API will be available at `http://localhost:5000`

### Frontend Setup (Modern React)

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## 📡 API Endpoints

### Base URL: `http://localhost:5000/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and documentation |
| GET | `/health` | Health check |
| POST | `/predict` | Analyze news article |

### POST /predict

**Request Body:**
```json
{
  "text": "Your news article text here..."
}
```

**Response:**
```json
{
  "prediction": "Real",
  "confidence": 0.89,
  "processed_text_length": 150,
  "reasons": null
}
```

For fake news, includes reasons:
```json
{
  "prediction": "Fake",
  "confidence": 0.76,
  "processed_text_length": 89,
  "reasons": [
    "Contains sensational language that may be clickbait",
    "Lacks credible source citations"
  ]
}
```

## 🔍 Analysis Features

The system analyzes news articles for:

- **Sensational Language**: Clickbait words and phrases
- **Conspiracy Theories**: Conspiracy-related terminology
- **Emotional Manipulation**: Fear-mongering tactics
- **Source Credibility**: Presence of reliable sources
- **Language Quality**: Informal or inappropriate language
- **Formatting Issues**: Excessive caps, punctuation
- **Content Structure**: Article length and repetition

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Lint Python code
flake8 app/

# Format code
black app/
```

### Environment Variables
```bash
export FLASK_ENV=development  # or production
export SECRET_KEY=your-secret-key
export PORT=5000
export HOST=0.0.0.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask, React, and scikit-learn
- Uses machine learning for news classification
- Modern web development practices