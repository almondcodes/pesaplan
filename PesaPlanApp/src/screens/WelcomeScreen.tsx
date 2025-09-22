import React from 'react';
import {
  View,
  StyleSheet,
  Dimensions,
  Image,
} from 'react-native';
import {
  Text,
  Button,
  Card,
  Surface,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { theme, typography, spacing, shadows } from '../utils/theme';

const { width, height } = Dimensions.get('window');

export default function WelcomeScreen() {
  const navigation = useNavigation();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Logo and Branding */}
        <View style={styles.logoContainer}>
          <Surface style={[styles.logoSurface, shadows.lg]}>
            <Text style={styles.logoText}>💰</Text>
          </Surface>
          <Text style={styles.appName}>PesaPlan</Text>
          <Text style={styles.tagline}>Automated Recurring Payments</Text>
        </View>

        {/* Features Card */}
        <Card style={[styles.featuresCard, shadows.md]}>
          <Card.Content>
            <Text style={styles.featuresTitle}>Why Choose PesaPlan?</Text>
            
            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>🔄</Text>
              <View style={styles.featureText}>
                <Text style={styles.featureTitle}>Automated Payments</Text>
                <Text style={styles.featureDescription}>
                  Set up recurring payments and never miss a bill again
                </Text>
              </View>
            </View>

            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>🔒</Text>
              <View style={styles.featureText}>
                <Text style={styles.featureTitle}>Secure & Reliable</Text>
                <Text style={styles.featureDescription}>
                  Bank-level security with M-Pesa integration
                </Text>
              </View>
            </View>

            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>📱</Text>
              <View style={styles.featureText}>
                <Text style={styles.featureTitle}>Easy to Use</Text>
                <Text style={styles.featureDescription}>
                  Simple interface designed for Kenyan users
                </Text>
              </View>
            </View>

            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>💡</Text>
              <View style={styles.featureText}>
                <Text style={styles.featureTitle}>Smart Management</Text>
                <Text style={styles.featureDescription}>
                  Track spending and manage your finances better
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Action Buttons */}
        <View style={styles.buttonContainer}>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Login' as never)}
            style={styles.primaryButton}
            contentStyle={styles.buttonContent}
            labelStyle={styles.buttonLabel}
          >
            Get Started
          </Button>
          
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('Register' as never)}
            style={styles.secondaryButton}
            contentStyle={styles.buttonContent}
            labelStyle={styles.secondaryButtonLabel}
          >
            Create Account
          </Button>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            By continuing, you agree to our Terms of Service and Privacy Policy
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: spacing.xxl,
    marginTop: spacing.xl,
  },
  logoSurface: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.primary,
    marginBottom: spacing.lg,
  },
  logoText: {
    fontSize: 48,
  },
  appName: {
    ...typography.h2,
    color: theme.colors.primary,
    fontWeight: 'bold',
    marginBottom: spacing.sm,
  },
  tagline: {
    ...typography.body1,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
  },
  featuresCard: {
    marginBottom: spacing.xxl,
    backgroundColor: theme.colors.surface,
  },
  featuresTitle: {
    ...typography.h4,
    color: theme.colors.onSurface,
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.lg,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: spacing.md,
    marginTop: 2,
  },
  featureText: {
    flex: 1,
  },
  featureTitle: {
    ...typography.h6,
    color: theme.colors.onSurface,
    marginBottom: spacing.xs,
  },
  featureDescription: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
    lineHeight: 20,
  },
  buttonContainer: {
    marginBottom: spacing.xl,
  },
  primaryButton: {
    marginBottom: spacing.md,
    backgroundColor: theme.colors.primary,
  },
  secondaryButton: {
    borderColor: theme.colors.primary,
  },
  buttonContent: {
    paddingVertical: spacing.sm,
  },
  buttonLabel: {
    ...typography.button,
    color: theme.colors.onPrimary,
  },
  secondaryButtonLabel: {
    ...typography.button,
    color: theme.colors.primary,
  },
  footer: {
    alignItems: 'center',
  },
  footerText: {
    ...typography.caption,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
    lineHeight: 16,
  },
});
