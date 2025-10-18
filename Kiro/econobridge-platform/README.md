# EconoBridge Platform

A digital economic bridge connecting rural micro-sellers to digital finance and trade using blockchain and AI.

## Features

- **Digital Wallet & Identity**: Unique wallet IDs for each user
- **Stable Token Payments**: Send/receive payments with 1% transaction fee
- **AI Credit Scoring**: Dynamic credit scores based on transaction history
- **Admin Dashboard**: Analytics and user management
- **Responsive UI**: Clean African fintech design with green/blue theme

## Tech Stack

- **Frontend**: React + Vite + TailwindCSS + Recharts
- **Backend**: Node.js + Express
- **Storage**: In-memory (easily replaceable with database)
- **Authentication**: JWT tokens

## Quick Start

1. **Install dependencies**:
   ```bash
   npm run install-all
   ```

2. **Start the application**:
   ```bash
   npm run dev
   ```

3. **Access the app**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001

## Demo Flow

1. **Register** a new user account
2. **View wallet** with starting balance of 1000 EBT
3. **Send money** to another wallet ID
4. **Watch credit score** update based on transaction history
5. **Check admin dashboard** for platform analytics

## API Endpoints

- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `GET /api/profile` - Get user profile with credit score
- `POST /api/send` - Send money to another wallet
- `GET /api/transactions` - Get user transactions
- `GET /api/admin/dashboard` - Admin analytics
- `POST /api/sms` - SMS transaction endpoint (demo)

## Credit Scoring Algorithm

The AI-powered credit scoring considers:
- Total number of transactions
- Days since account registration
- Average transaction amount
- Transaction frequency

Score ranges from 0-100 with color coding:
- Green (80-100): Excellent
- Yellow (60-79): Good
- Red (0-59): Poor

## Test Users

Create multiple accounts to test money transfers and see the admin dashboard populate with user data and analytics.

## Future Enhancements

- Real blockchain integration (Polkadot/Substrate)
- Database persistence (MongoDB/Supabase)
- SMS gateway integration
- Mobile app version
- Advanced ML models for credit scoring
