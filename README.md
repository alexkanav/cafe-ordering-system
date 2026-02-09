# Cafe Ordering System (Flask + FastAPI + React)

## A hybrid backend architecture combining Flask and FastAPI, paired with a React SPA, demonstrating consistent implementation of JWT authentication, caching, and rate limiting across both frameworks using Domain-Driven Design (DDD) principles.

### Designed for real-world café workflows. Suitable for production use, learning purposes, and architectural experimentation.

---
## Architecture Overview
- **Flask** – legacy-friendly and core synchronous operations
- **FastAPI** – modern, async, high-performance APIs
- **React** – responsive Single Page Application for customers, staff, and administrators

The system cleanly separates concerns while allowing both frameworks to coexist under a unified domain model.

---
## Authentication, Caching & Rate Limiting
### Flask Implementation

#### JWT Authentication
- flask-jwt-extended
- Access & refresh tokens
- Route protection via decorators

#### Caching
- flask-caching
- Pluggable backends:
  * Redis
  * Filesystem
  * In-memory 

#### Rate Limiting
- flask-limiter
- IP-based limits using get_remote_address

### FastAPI Implementation
#### JWT Authentication
- python-jose
- Stateless token verification
- Dependency-based route protection

#### Caching
- fastapi-cache
- Redis backend (production)
- In-memory backend (development/testing)

#### Rate Limiting
- Custom rate limiter built on SlowAPI
- IP-based limits using get_remote_address
 
---
## Domain-Driven Design Layers
- **Domain** → Pure business logic (framework-agnostic)
- **Application / Transport** → Flask & FastAPI layers
- **Infrastructure** → Database and external services
- **Presentation** → React frontend
This separation ensures testability, scalability, and long-term maintainability.

---
## Features
- Role-based access control via JWT
- Admin panel for menu and system management
- Coupon and discount system with regular customer tracking
- Analytics dashboard
- Staff board for real-time order management
- Clean, responsive UI for all user roles

---
## Database Support
### Persistent storage with support for:
- SQLite
- PostgreSQL
- MySQL

---
## Setup & Run Instructions
### Prerequisites
- Python 3.10+
- Node.js 18+ (for React frontend)
- Redis (optional, required for production caching & rate limiting)

### Backend Setup
#### 1. Create and activate a virtual environment
```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```
#### 3. Environment configuration
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
REDIS_URL=redis://localhost:6379/0
```
Both Flask and FastAPI share configuration values where applicable.

### Frontend Setup (Vite + React)
```bash
cd frontend
npm install
npm run dev
```
---
### Running the Services
#### Run Flask API
```bash
flask run
```

#### Run FastAPI API
```bash
uvicorn fastapi_app.main:app --reload
```

Flask and FastAPI run as independent services and can be started separately or together.

---
## Production Deployment
- Flask: WSGI server (Gunicorn / uWSGI)
- FastAPI: ASGI server (Uvicorn / Hypercorn)
- Reverse proxy (e.g., Nginx)
- Environment-based configuration
- Optional Docker containerization

---
## License
#### MIT License
Free to use, modify, and distribute.
