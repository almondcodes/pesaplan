# PesaPlan Mobile App

A React Native mobile application for automated recurring payments in Kenya using M-Pesa integration.

## Features

- **User Authentication**: Phone number-based login and registration
- **Wallet Management**: View balance, transaction history, and manage funds
- **Standing Orders**: Set up and manage recurring payments
- **M-Pesa Integration**: Seamless payment processing
- **Secure Storage**: Biometric authentication and secure token storage
- **Modern UI**: Material Design 3 with React Native Paper

## Tech Stack

- **React Native** with Expo
- **TypeScript** for type safety
- **React Navigation** for navigation
- **React Native Paper** for UI components
- **React Query** for data fetching and caching
- **Expo Secure Store** for secure token storage
- **Expo Local Authentication** for biometric auth

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Expo CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PesaPlanApp
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Run on your preferred platform:
```bash
# Android
npm run android

# iOS (macOS only)
npm run ios

# Web
npm run web
```

## Project Structure

```
src/
├── components/          # Reusable UI components
├── screens/            # Screen components
├── navigation/         # Navigation configuration
├── services/           # API services and utilities
├── utils/              # Utility functions and theme
├── types/              # TypeScript type definitions
├── hooks/              # Custom React hooks
└── contexts/           # React contexts (Auth, etc.)
```

## Key Features Implementation

### Authentication
- Phone number-based authentication
- JWT token management
- Secure token storage with Expo Secure Store
- Biometric authentication support

### Wallet Management
- Real-time balance display
- Transaction history
- Deposit and withdrawal functionality
- M-Pesa integration

### Standing Orders
- Create, edit, and manage recurring payments
- Multiple frequency options (daily, weekly, monthly, etc.)
- Payment method selection (wallet, M-Pesa, or both)
- Execution tracking and notifications

### Security
- Secure token storage
- Biometric authentication
- API request encryption
- Input validation and sanitization

## API Integration

The app integrates with the PesaPlan backend API:

- **Base URL**: `http://localhost:8000/api/v1/`
- **Authentication**: JWT tokens
- **Endpoints**:
  - `/auth/` - Authentication (login, register, refresh)
  - `/wallets/` - Wallet management
  - `/standing-orders/` - Standing orders
  - `/transactions/` - Transaction history
  - `/payments/` - Payment processing

## Development

### Running Tests
```bash
npm test
```

### Building for Production
```bash
# Android
eas build --platform android

# iOS
eas build --platform ios
```

### Code Style
- ESLint for code linting
- Prettier for code formatting
- TypeScript for type checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
