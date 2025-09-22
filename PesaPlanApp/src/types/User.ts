export interface User {
  id: string;
  phone_number: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  status: 'pending_verification' | 'active' | 'suspended' | 'deactivated';
  user_type: 'individual' | 'business';
  language: string;
  timezone: string;
  created_at: string;
  updated_at: string;
  phone_verified_at?: string;
  email_verified_at?: string;
  last_login?: string;
}

export interface UserProfile {
  id: string;
  user: string;
  bio?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  address_line_1?: string;
  address_line_2?: string;
  city?: string;
  county?: string;
  country: string;
  postal_code?: string;
  profile_picture?: string;
  created_at: string;
  updated_at: string;
}

export interface Wallet {
  id: string;
  user: string;
  balance: string;
  phone_number: string;
  status: 'active' | 'suspended' | 'closed';
  daily_limit: string;
  monthly_limit: string;
  transaction_limit: string;
  created_at: string;
  updated_at: string;
}

export interface WalletTransaction {
  id: string;
  wallet: string;
  transaction_type: 'deposit' | 'withdrawal' | 'transfer_in' | 'transfer_out' | 'fee' | 'refund';
  amount: string;
  balance_before: string;
  balance_after: string;
  description: string;
  reference: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface StandingOrder {
  id: string;
  user: string;
  wallet: string;
  title: string;
  amount: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  payment_method: 'wallet' | 'mpesa' | 'both';
  recipient_name: string;
  recipient_phone: string;
  recipient_account?: string;
  start_date: string;
  end_date?: string;
  next_execution: string;
  last_execution?: string;
  status: 'active' | 'paused' | 'cancelled' | 'completed' | 'failed';
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  max_executions?: number;
  max_amount?: string;
  created_at: string;
  updated_at: string;
}

export interface StandingOrderExecution {
  id: string;
  standing_order: string;
  amount: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  execution_date: string;
  transaction_reference?: string;
  error_message?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  wallet: string;
  transaction_type: 'deposit' | 'withdrawal' | 'transfer' | 'payment' | 'refund' | 'fee';
  amount: string;
  currency: string;
  description: string;
  reference: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  recipient_name?: string;
  recipient_phone?: string;
  recipient_account?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  user: string;
  type: 'payment' | 'standing_order' | 'wallet' | 'system' | 'security';
  title: string;
  message: string;
  is_read: boolean;
  data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

// Form Types
export interface LoginForm {
  phoneNumber: string;
  password: string;
}

export interface RegisterForm {
  phoneNumber: string;
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  passwordConfirm: string;
}

export interface ChangePasswordForm {
  oldPassword: string;
  newPassword: string;
  newPasswordConfirm: string;
}

export interface CreateStandingOrderForm {
  title: string;
  amount: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  recipientName: string;
  recipientPhone: string;
  recipientAccount?: string;
  startDate: string;
  endDate?: string;
  maxExecutions?: number;
  maxAmount?: string;
}

export interface TransferForm {
  amount: string;
  recipientPhone: string;
  description: string;
}

export interface DepositForm {
  amount: string;
  paymentMethod: 'mpesa' | 'bank_transfer' | 'card';
  description: string;
}
