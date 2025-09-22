import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  Surface,
  ActivityIndicator,
  Checkbox,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import { theme, typography, spacing, shadows } from '../utils/theme';

export default function RegisterScreen() {
  const navigation = useNavigation();
  const { register, isLoading } = useAuth();
  
  const [formData, setFormData] = useState({
    phoneNumber: '',
    email: '',
    firstName: '',
    lastName: '',
    password: '',
    passwordConfirm: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (!/^\+254\d{9}$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = 'Please enter a valid Kenyan phone number (+254XXXXXXXXX)';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!formData.passwordConfirm.trim()) {
      newErrors.passwordConfirm = 'Please confirm your password';
    } else if (formData.password !== formData.passwordConfirm) {
      newErrors.passwordConfirm = 'Passwords do not match';
    }

    if (!agreeToTerms) {
      newErrors.terms = 'You must agree to the Terms of Service and Privacy Policy';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    try {
      await register(formData);
      // Navigation will be handled by AuthContext
    } catch (error) {
      Alert.alert(
        'Registration Failed',
        error instanceof Error ? error.message : 'An error occurred during registration',
        [{ text: 'OK' }]
      );
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <Surface style={[styles.logoSurface, shadows.md]}>
              <Text style={styles.logoText}>💰</Text>
            </Surface>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>Join PesaPlan and start managing your payments</Text>
          </View>

          {/* Registration Form */}
          <Card style={[styles.formCard, shadows.md]}>
            <Card.Content>
              <View style={styles.nameRow}>
                <TextInput
                  label="First Name"
                  value={formData.firstName}
                  onChangeText={(value) => handleInputChange('firstName', value)}
                  mode="outlined"
                  error={!!errors.firstName}
                  style={[styles.input, styles.halfInput]}
                  left={<TextInput.Icon icon="account" />}
                  autoCapitalize="words"
                  autoComplete="given-name"
                />
                <TextInput
                  label="Last Name"
                  value={formData.lastName}
                  onChangeText={(value) => handleInputChange('lastName', value)}
                  mode="outlined"
                  error={!!errors.lastName}
                  style={[styles.input, styles.halfInput]}
                  left={<TextInput.Icon icon="account" />}
                  autoCapitalize="words"
                  autoComplete="family-name"
                />
              </View>
              {errors.firstName && (
                <Text style={styles.errorText}>{errors.firstName}</Text>
              )}
              {errors.lastName && (
                <Text style={styles.errorText}>{errors.lastName}</Text>
              )}

              <TextInput
                label="Phone Number"
                value={formData.phoneNumber}
                onChangeText={(value) => handleInputChange('phoneNumber', value)}
                mode="outlined"
                keyboardType="phone-pad"
                placeholder="+254XXXXXXXXX"
                error={!!errors.phoneNumber}
                style={styles.input}
                left={<TextInput.Icon icon="phone" />}
                autoCapitalize="none"
                autoComplete="tel"
              />
              {errors.phoneNumber && (
                <Text style={styles.errorText}>{errors.phoneNumber}</Text>
              )}

              <TextInput
                label="Email Address"
                value={formData.email}
                onChangeText={(value) => handleInputChange('email', value)}
                mode="outlined"
                keyboardType="email-address"
                error={!!errors.email}
                style={styles.input}
                left={<TextInput.Icon icon="email" />}
                autoCapitalize="none"
                autoComplete="email"
              />
              {errors.email && (
                <Text style={styles.errorText}>{errors.email}</Text>
              )}

              <TextInput
                label="Password"
                value={formData.password}
                onChangeText={(value) => handleInputChange('password', value)}
                mode="outlined"
                secureTextEntry={!showPassword}
                error={!!errors.password}
                style={styles.input}
                left={<TextInput.Icon icon="lock" />}
                right={
                  <TextInput.Icon
                    icon={showPassword ? 'eye-off' : 'eye'}
                    onPress={() => setShowPassword(!showPassword)}
                  />
                }
                autoCapitalize="none"
                autoComplete="new-password"
              />
              {errors.password && (
                <Text style={styles.errorText}>{errors.password}</Text>
              )}

              <TextInput
                label="Confirm Password"
                value={formData.passwordConfirm}
                onChangeText={(value) => handleInputChange('passwordConfirm', value)}
                mode="outlined"
                secureTextEntry={!showPasswordConfirm}
                error={!!errors.passwordConfirm}
                style={styles.input}
                left={<TextInput.Icon icon="lock-check" />}
                right={
                  <TextInput.Icon
                    icon={showPasswordConfirm ? 'eye-off' : 'eye'}
                    onPress={() => setShowPasswordConfirm(!showPasswordConfirm)}
                  />
                }
                autoCapitalize="none"
                autoComplete="new-password"
              />
              {errors.passwordConfirm && (
                <Text style={styles.errorText}>{errors.passwordConfirm}</Text>
              )}

              {/* Terms and Conditions */}
              <View style={styles.termsContainer}>
                <Checkbox
                  status={agreeToTerms ? 'checked' : 'unchecked'}
                  onPress={() => setAgreeToTerms(!agreeToTerms)}
                />
                <View style={styles.termsText}>
                  <Text style={styles.termsTextContent}>
                    I agree to the{' '}
                    <Text
                      style={styles.termsLink}
                      onPress={() => {
                        // TODO: Open terms of service
                        Alert.alert('Terms of Service', 'This will open the Terms of Service');
                      }}
                    >
                      Terms of Service
                    </Text>
                    {' '}and{' '}
                    <Text
                      style={styles.termsLink}
                      onPress={() => {
                        // TODO: Open privacy policy
                        Alert.alert('Privacy Policy', 'This will open the Privacy Policy');
                      }}
                    >
                      Privacy Policy
                    </Text>
                  </Text>
                </View>
              </View>
              {errors.terms && (
                <Text style={styles.errorText}>{errors.terms}</Text>
              )}

              <Button
                mode="contained"
                onPress={handleRegister}
                disabled={isLoading}
                style={styles.registerButton}
                contentStyle={styles.buttonContent}
                labelStyle={styles.buttonLabel}
              >
                {isLoading ? (
                  <ActivityIndicator color={theme.colors.onPrimary} size="small" />
                ) : (
                  'Create Account'
                )}
              </Button>
            </Card.Content>
          </Card>

          {/* Sign In Link */}
          <View style={styles.signinContainer}>
            <Text style={styles.signinText}>Already have an account? </Text>
            <Button
              mode="text"
              onPress={() => navigation.navigate('Login' as never)}
              labelStyle={styles.signinButtonText}
            >
              Sign In
            </Button>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.xl,
    marginTop: spacing.lg,
  },
  logoSurface: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.primary,
    marginBottom: spacing.lg,
  },
  logoText: {
    fontSize: 36,
  },
  title: {
    ...typography.h3,
    color: theme.colors.onBackground,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
  },
  formCard: {
    marginBottom: spacing.xl,
    backgroundColor: theme.colors.surface,
  },
  nameRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfInput: {
    flex: 0.48,
  },
  input: {
    marginBottom: spacing.md,
  },
  errorText: {
    ...typography.caption,
    color: theme.colors.error,
    marginTop: -spacing.sm,
    marginBottom: spacing.sm,
  },
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.lg,
  },
  termsText: {
    flex: 1,
    marginLeft: spacing.sm,
  },
  termsTextContent: {
    ...typography.caption,
    color: theme.colors.onSurfaceVariant,
    lineHeight: 16,
  },
  termsLink: {
    color: theme.colors.primary,
    textDecorationLine: 'underline',
  },
  registerButton: {
    backgroundColor: theme.colors.primary,
    marginBottom: spacing.md,
  },
  buttonContent: {
    paddingVertical: spacing.sm,
  },
  buttonLabel: {
    ...typography.button,
    color: theme.colors.onPrimary,
  },
  signinContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  signinText: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
  },
  signinButtonText: {
    ...typography.body2,
    color: theme.colors.primary,
    fontWeight: '600',
  },
});
