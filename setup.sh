#!/bin/bash
# ===========================================
# Doomly Deployment Setup Script
# ===========================================

set -e

echo "=========================================="
echo "  Doomly Event Management - Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print warning
warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    success "Python $PYTHON_VERSION found"
else
    error "Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    success "pip3 found"
else
    error "pip3 not found. Please install pip"
    exit 1
fi

# Check Node.js (for frontend)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    success "Node.js v$NODE_VERSION found"
else
    warn "Node.js not found. Frontend build will require manual setup."
fi

echo ""
echo "=========================================="
echo "  Setting up Backend"
echo "=========================================="

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    success "Virtual environment created"
else
    success "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-prod.txt
success "Dependencies installed"

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    success ".env file created"
    echo ""
    warn "Please edit .env and add your configuration values:"
    echo "  - SECRET_KEY"
    echo "  - JWT_SECRET_KEY"
    echo "  - DATABASE_URL"
    echo "  - MAIL settings"
else
    success ".env file already exists"
fi

# Initialize database
echo ""
echo "Initializing database..."
flask db init 2>/dev/null || true
flask db migrate -m "Initial migration"
flask db upgrade
success "Database initialized"

# Deactivate virtual environment
deactivate

echo ""
echo "=========================================="
echo "  Setting up Frontend"
echo "=========================================="

cd ../frontend

if [ -f "package.json" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    success "Frontend dependencies installed"
else
    warn "Frontend package.json not found"
fi

cd ..

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "To start development:"
echo "  cd doomly"
echo "  docker-compose up"
echo ""
echo "Or manually:"
echo "  Backend: cd backend && source venv/bin/activate && flask run"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "For production deployment, see DEPLOY.md"
echo ""
