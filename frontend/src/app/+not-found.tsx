import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Link, Stack } from 'expo-router';
import { colors, spacing, typography } from '../theme';
import { AppShell } from '../components/layout/AppShell';
import { PageContainer } from '../components/layout/PageContainer';

export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ title: 'Não Encontrado' }} />
      <AppShell>
        <PageContainer scrollable={false}>
          <View style={styles.container}>
            <Text style={styles.emoji}>🧐</Text>
            <Text style={styles.title}>Página não encontrada</Text>
            <Text style={styles.message}>
              A página que você está procurando não existe ou foi movida.
            </Text>
            <Link href="/" style={styles.link}>
              <Text style={styles.linkText}>Voltar para o Início ➔</Text>
            </Link>
          </View>
        </PageContainer>
      </AppShell>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  emoji: {
    fontSize: 64,
    marginBottom: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.xl,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  message: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.xl,
    maxWidth: 350,
    lineHeight: typography.lineHeight.sm,
  },
  link: {
    marginTop: spacing.md,
    paddingVertical: spacing.md,
  },
  linkText: {
    fontSize: typography.fontSize.md,
    color: colors.primary,
    fontFamily: typography.fontFamily.bold,
  },
});
