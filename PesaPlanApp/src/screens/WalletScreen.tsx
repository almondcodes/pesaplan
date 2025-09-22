import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { theme, typography, spacing } from '../utils/theme';

export default function WalletScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Wallet</Text>
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.cardText}>Wallet management features coming soon...</Text>
          </Card.Content>
        </Card>
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
    padding: spacing.lg,
  },
  title: {
    ...typography.h3,
    color: theme.colors.onBackground,
    marginBottom: spacing.lg,
  },
  card: {
    backgroundColor: theme.colors.surface,
  },
  cardText: {
    ...typography.body1,
    color: theme.colors.onSurface,
  },
});
