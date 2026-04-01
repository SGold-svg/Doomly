# Doomly - Event Management Platform

A comprehensive event management platform built with Vue.js frontend and Python/Flask backend.

## Features

### Event Management
- Create and manage events with detailed information
- Event types: conferences, workshops, webinars, concerts, meetups
- Online and offline event support
- Custom branding (logos, banners)
- SEO optimization settings

### Ticketing
- Multiple ticket types per event
- Free and paid tickets
- Quantity limits and sales windows
- Promo codes and discounts (percentage or fixed)
- Capacity management

### Attendees
- Registration with custom fields
- QR code check-in
- Badge printing support
- CSV export
- Attendee search and filtering

### Orders
- Complete checkout flow
- Order management
- Order status tracking
- Refund support

### Dashboard & Analytics
- Revenue tracking
- Sales statistics
- Check-in rates
- Recent activity

### Email
- Email templates
- Confirmation emails
- Reminder emails
- Custom email campaigns

## Tech Stack

### Backend
- Python 3.10+
- Flask
- SQLAlchemy
- Flask-JWT-Extended (Authentication)
- Flask-CORS
- Flask-Migrate

### Frontend
- Vue.js 3
- Vue Router
- Pinia (State Management)
- Tailwind CSS
- Vite

## Quick Start

### Backend Setup

```bash
cd doomly/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

The backend will be available at http://localhost:5000

### Frontend Setup

```bash
cd doomly/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Events
- `GET /api/events` - List public events
- `GET /api/events/:slug` - Get event by slug
- `GET /api/events/my-events` - Get user's events
- `POST /api/events` - Create event
- `PUT /api/events/:id` - Update event
- `DELETE /api/events/:id` - Delete event
- `POST /api/events/:id/publish` - Publish event

### Tickets
- `GET /api/tickets/event/:id` - Get event tickets
- `POST /api/tickets/event/:id` - Create ticket type
- `PUT /api/tickets/:id` - Update ticket
- `DELETE /api/tickets/:id` - Delete ticket

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders/:number` - Get order
- `GET /api/orders/my-orders` - Get user's orders
- `GET /api/orders/event/:id` - Get event orders

### Attendees
- `GET /api/attendees/event/:id` - Get event attendees
- `GET /api/attendees/:id` - Get attendee
- `POST /api/attendees/:id/check-in` - Check in attendee
- `POST /api/attendees/ticket/:number/check-in` - Check in by ticket number

### Dashboard
- `GET /api/dashboard/overview` - Get overview stats
- `GET /api/dashboard/event/:id` - Get event stats

## Environment Variables

Create a `.env` file in the backend directory:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///doomly.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-app-password
```

## Project Structure

```
doomly/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes/
│   │           ├── auth.py
│   │           ├── events.py
│   │           ├── tickets.py
│   │           ├── orders.py
│   │           ├── attendees.py
│   │           ├── users.py
│   │           ├── organizations.py
│   │           ├── emails.py
│   │           ├── checkin.py
│   │           ├── dashboard.py
│   │           └── settings.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── style.css
│   │   ├── api/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   └── router/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

## License

MIT License
