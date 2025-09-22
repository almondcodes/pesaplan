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
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import { theme, typography, spacing, shadows } from '../utils/theme';

export default function LoginScreen() {
  const navigation = useNavigation();
  const { login, isLoading } = useAuth();
  
  const [formData, setFormData] = useState({
    phoneNumber: '',
    password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (!/^\+254\d{9}$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = 'Please enter a valid Kenyan phone number (+254XXXXXXXXX)';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async () => {
    if (!validateForm()) return;

    try {
      await login(formData.phoneNumber, formData.password);
      // Navigation will be handled by AuthContext
    } catch (error) {
      Alert.alert(
        'Login Failed',
        error instanceof Error ? error.message : 'An error occurred during login',
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
            <Text style={styles.title}>Welcome Back</Text>
            <Text style={styles.subtitle}>Sign in to your PesaPlan account</Text>
          </View>

          {/* Login Form */}
          <Card style={[styles.formCard, shadows.md]}>
            <Card.Content>
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
                autoComplete="password"
              />
              {errors.password && (
                <Text style={styles.errorText}>{errors.password}</Text>
              )}

              <Button
                mode="text"
                onPress={() => {
                  // TODO: Implement forgot password
                  Alert.alert('Forgot Password', 'This feature will be available soon');
                }}
                style={styles.forgotPasswordButton}
                labelStyle={styles.forgotPasswordText}
              >
                Forgot Password?
              </Button>

              <Button
                mode="contained"
                onPress={handleLogin}
                disabled={isLoading}
                style={styles.loginButton}
                contentStyle={styles.buttonContent}
                labelStyle={styles.buttonLabel}
              >
                {isLoading ? (
                  <ActivityIndicator color={theme.colors.onPrimary} size="small" />
                ) : (
                  'Sign In'
                )}
              </Button>
            </Card.Content>
          </Card>

          {/* Sign Up Link */}
          <View style={styles.signupContainer}>
            <Text style={styles.signupText}>Don't have an account? </Text>
            <Button
              mode="text"
              onPress={() => navigation.navigate('Register' as never)}
              labelStyle={styles.signupButtonText}
            >
              Sign Up
            </Button>
          </View>

          {/* Demo Credentials */}
          <Card style={[styles.demoCard, shadows.sm]}>
            <Card.Content>
              <Text style={styles.demoTitle}>Demo Credentials</Text>
              <Text style={styles.demoText}>
                Phone: +254712345678{'\n'}
                Password: testpass123
              </Text>
            </Card.Content>
          </Card>
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
    marginBottom: spacing.xxl,
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
  input: {
    marginBottom: spacing.md,
  },
  errorText: {
    ...typography.caption,
    color: theme.colors.error,
    marginTop: -spacing.sm,
    marginBottom: spacing.sm,
  },
  forgotPasswordButton: {
    alignSelf: 'flex-end',
    marginBottom: spacing.lg,
  },
  forgotPasswordText: {
    ...typography.caption,
    color: theme.colors.primary,
  },
  loginButton: {
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
  signupContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  signupText: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
  },
  signupButtonText: {
    ...typography.body2,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  demoCard: {
    backgroundColor: theme.colors.surfaceVariant,
  },
  demoTitle: {
    ...typography.h6,
    color: theme.colors.onSurfaceVariant,
    marginBottom: spacing.sm,
  },
  demoText: {
    ...typography.caption,
    color: theme.colors.onSurfaceVariant,
    fontFamily: 'monospace',
  },
});
