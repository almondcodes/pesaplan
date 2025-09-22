import React from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
} from 'react-native';
import {
  Text,
  Card,
  Surface,
  Button,
  FAB,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import { theme, typography, spacing, shadows } from '../utils/theme';

export default function DashboardScreen() {
  const navigation = useNavigation();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Hello,</Text>
            <Text style={styles.userName}>{user?.first_name || 'User'}</Text>
          </View>
          <Button
            mode="outlined"
            onPress={handleLogout}
            style={styles.logoutButton}
            labelStyle={styles.logoutButtonLabel}
          >
            Logout
          </Button>
        </View>

        {/* Wallet Balance Card */}
        <Card style={[styles.balanceCard, shadows.lg]}>
          <Card.Content>
            <Text style={styles.balanceLabel}>Wallet Balance</Text>
            <Text style={styles.balanceAmount}>KES 0.00</Text>
            <Text style={styles.balanceSubtext}>Available for transactions</Text>
          </Card.Content>
        </Card>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionGrid}>
            <Card style={[styles.actionCard, shadows.sm]}>
              <Card.Content style={styles.actionContent}>
                <Text style={styles.actionIcon}>💳</Text>
                <Text style={styles.actionTitle}>Add Money</Text>
              </Card.Content>
            </Card>
            
            <Card style={[styles.actionCard, shadows.sm]}>
              <Card.Content style={styles.actionContent}>
                <Text style={styles.actionIcon}>📤</Text>
                <Text style={styles.actionTitle}>Send Money</Text>
              </Card.Content>
            </Card>
            
            <Card style={[styles.actionCard, shadows.sm]}>
              <Card.Content style={styles.actionContent}>
                <Text style={styles.actionIcon}>🔄</Text>
                <Text style={styles.actionTitle}>Standing Orders</Text>
              </Card.Content>
            </Card>
            
            <Card style={[styles.actionCard, shadows.sm]}>
              <Card.Content style={styles.actionContent}>
                <Text style={styles.actionIcon}>📊</Text>
                <Text style={styles.actionTitle}>Analytics</Text>
              </Card.Content>
            </Card>
          </View>
        </View>

        {/* Recent Transactions */}
        <View style={styles.recentTransactions}>
          <Text style={styles.sectionTitle}>Recent Transactions</Text>
          <Card style={[styles.transactionsCard, shadows.sm]}>
            <Card.Content>
              <View style={styles.emptyState}>
                <Text style={styles.emptyIcon}>📝</Text>
                <Text style={styles.emptyTitle}>No transactions yet</Text>
                <Text style={styles.emptySubtext}>
                  Your transaction history will appear here
                </Text>
              </View>
            </Card.Content>
          </Card>
        </View>

        {/* Standing Orders */}
        <View style={styles.standingOrders}>
          <Text style={styles.sectionTitle}>Active Standing Orders</Text>
          <Card style={[styles.standingOrdersCard, shadows.sm]}>
            <Card.Content>
              <View style={styles.emptyState}>
                <Text style={styles.emptyIcon}>⏰</Text>
                <Text style={styles.emptyTitle}>No standing orders</Text>
                <Text style={styles.emptySubtext}>
                  Set up recurring payments to automate your bills
                </Text>
                <Button
                  mode="contained"
                  onPress={() => navigation.navigate('StandingOrders' as never)}
                  style={styles.setupButton}
                  labelStyle={styles.setupButtonLabel}
                >
                  Set Up Standing Order
                </Button>
              </View>
            </Card.Content>
          </Card>
        </View>
      </ScrollView>

      {/* Floating Action Button */}
      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => {
          // TODO: Show action sheet for quick actions
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
    paddingBottom: 100, // Space for FAB
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  greeting: {
    ...typography.body1,
    color: theme.colors.onSurfaceVariant,
  },
  userName: {
    ...typography.h4,
    color: theme.colors.onBackground,
    fontWeight: 'bold',
  },
  logoutButton: {
    borderColor: theme.colors.outline,
  },
  logoutButtonLabel: {
    ...typography.caption,
    color: theme.colors.onSurfaceVariant,
  },
  balanceCard: {
    backgroundColor: theme.colors.primary,
    marginBottom: spacing.xl,
  },
  balanceLabel: {
    ...typography.body2,
    color: theme.colors.onPrimary,
    opacity: 0.8,
  },
  balanceAmount: {
    ...typography.h2,
    color: theme.colors.onPrimary,
    fontWeight: 'bold',
    marginVertical: spacing.sm,
  },
  balanceSubtext: {
    ...typography.caption,
    color: theme.colors.onPrimary,
    opacity: 0.8,
  },
  quickActions: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    ...typography.h5,
    color: theme.colors.onBackground,
    marginBottom: spacing.md,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionCard: {
    width: '48%',
    marginBottom: spacing.md,
    backgroundColor: theme.colors.surface,
  },
  actionContent: {
    alignItems: 'center',
    paddingVertical: spacing.lg,
  },
  actionIcon: {
    fontSize: 32,
    marginBottom: spacing.sm,
  },
  actionTitle: {
    ...typography.body2,
    color: theme.colors.onSurface,
    textAlign: 'center',
  },
  recentTransactions: {
    marginBottom: spacing.xl,
  },
  transactionsCard: {
    backgroundColor: theme.colors.surface,
  },
  standingOrders: {
    marginBottom: spacing.xl,
  },
  standingOrdersCard: {
    backgroundColor: theme.colors.surface,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: spacing.md,
    opacity: 0.5,
  },
  emptyTitle: {
    ...typography.h6,
    color: theme.colors.onSurfaceVariant,
    marginBottom: spacing.sm,
  },
  emptySubtext: {
    ...typography.body2,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  setupButton: {
    backgroundColor: theme.colors.primary,
  },
  setupButtonLabel: {
    ...typography.button,
    color: theme.colors.onPrimary,
  },
  fab: {
    position: 'absolute',
    margin: spacing.lg,
    right: 0,
    bottom: 0,
    backgroundColor: theme.colors.primary,
  },
});
