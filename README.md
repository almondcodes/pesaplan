# PesaPlan

Automated recurring payments for Kenya with M-Pesa. Django REST backend for standing orders, wallets, and payment processing; React Native mobile app planned.

## Features

### Core
- **User Management**: Phone-based authentication with JWT tokens
- **Wallet System**: Digital wallet with balance tracking and transaction history
- **Standing Orders**: Automated recurring payments (daily, weekly, monthly, etc.)
- **M-Pesa Integration**: STK Push, C2B, and B2C payment processing
- **Transaction Management**: Comprehensive transaction tracking and audit logs
- **Notification System**: SMS, email, and push notifications
- **Security**: PIN-based authentication, rate limiting, and audit trails

### Advanced
- **Background Jobs**: Celery-based task processing for payment automation
- **Retry Logic**: Automatic retry for failed payments
- **Compliance**: Audit logs and transaction traceability
- **Scalability**: Redis caching and PostgreSQL database
- **Monitoring**: Health checks and comprehensive logging

## Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database
- **Redis** - Caching and Celery broker
- **Celery** - Background task processing
- **M-Pesa Daraja API** - Payment processing

### Frontend (planned)
- **React Native** - Mobile application
- **React.js** - Admin dashboard

## Project structure

```
pesaplan/
├── backend/
│   ├── pesaplan/
│   │   ├── apps/
│   │   │   ├── users/           # User management
│   │   │   ├── wallets/         # Wallet operations
│   │   │   ├── standing_orders/ # Recurring payments
│   │   │   ├── transactions/    # Transaction tracking
│   │   │   ├── payments/        # M-Pesa integration
│   │   │   └── notifications/   # Communication system
│   │   ├── settings/            # Environment-specific settings
│   │   ├── utils/               # Utility functions
│   │   └── requirements/        # Python dependencies
│   ├── docker-compose.yml       # Development environment
│   ├── Dockerfile              # Production container
│   └── manage.py               # Django management
├── mobile/                     # React Native app (planned)
├── admin-dashboard/            # React admin panel (planned)
└── docs/                       # Documentation
```

## Quick start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Development setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/almondcodes/pesaplan.git
   cd pesaplan
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements/development.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Set up the database**
   ```bash
   python manage.py migrate
   python manage.py create_superuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup (Recommended)

1. **Start all services**
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py create_superuser
   ```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=pesaplan
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# M-Pesa (Get from Safaricom)
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://your-domain.com/api/v1/payments/mpesa/callback/
MPESA_ENVIRONMENT=sandbox

# Africa's Talking (SMS)
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key
```

## API documentation

### Authentication Endpoints
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/profile/` - User profile

### Wallet Endpoints
- `GET /api/v1/wallets/` - Get wallet details
- `GET /api/v1/wallets/balance/` - Get wallet balance
- `POST /api/v1/wallets/topup/` - Top up wallet
- `POST /api/v1/wallets/withdraw/` - Withdraw from wallet
- `POST /api/v1/wallets/transfer/` - Transfer to another user

### Standing Orders Endpoints
- `GET /api/v1/standing-orders/` - List standing orders
- `POST /api/v1/standing-orders/` - Create standing order
- `GET /api/v1/standing-orders/{id}/` - Get standing order details
- `PUT /api/v1/standing-orders/{id}/` - Update standing order
- `DELETE /api/v1/standing-orders/{id}/` - Cancel standing order
- `POST /api/v1/standing-orders/{id}/execute/` - Execute standing order

## Security

- **JWT Authentication**: Secure token-based authentication
- **PIN Protection**: 4-6 digit PIN for sensitive operations
- **Rate Limiting**: API rate limiting to prevent abuse
- **Audit Logs**: Comprehensive logging of all transactions
- **Data Encryption**: Sensitive data encryption at rest
- **HTTPS Enforcement**: SSL/TLS in production

## Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Deployment

### Production Deployment

1. **Configure production settings**
   ```bash
   cp env.example .env
   # Update with production values
   ```

2. **Build and deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Collect static files**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### Environment-Specific Settings

- **Development**: `pesaplan.settings.development`
- **Production**: `pesaplan.settings.production`

## Monitoring

### Health Checks
- `GET /health/` - Comprehensive health check endpoint

### Logging
- Application logs: `/app/logs/django.log`
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints

## Roadmap

### Phase 1: Backend Foundation ✅
- [x] Django project setup
- [x] User management system
- [x] Wallet system
- [x] Standing orders
- [x] M-Pesa integration
- [x] Background job processing

### Phase 2: Mobile App (In Progress)
- [ ] React Native app
- [ ] User authentication
- [ ] Wallet management
- [ ] Standing order creation
- [ ] Transaction history

### Phase 3: Admin Dashboard
- [ ] React admin panel
- [ ] User management
- [ ] Transaction monitoring
- [ ] Analytics dashboard

### Phase 4: Advanced Features
- [ ] Group standing orders
- [ ] Savings goals
- [ ] Investment features
- [ ] API for third-party integration

---

**Built with ❤️ for the Kenyan fintech ecosystem**
