import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { StandingsWidget } from './StandingsWidget';
import { HighlightCard } from './HighlightCard';
import { LeaderboardCard } from './LeaderboardCard';
import { colors, spacing, typography } from '../../theme';
import { useResponsive } from '../../hooks/useResponsive';
import { Link } from 'expo-router';

export const HomeScreen: React.FC = () => {
  const { isMobile } = useResponsive();

  return (
    <AppShell>
      <PageContainer>
        {/* Layout de duas colunas responsivo */}
        <View style={[styles.layoutGrid, isMobile && styles.layoutColumn]}>
          {/* Coluna da Esquerda: Classificação */}
          <View style={[styles.column, { flex: 4 }]}>
            <StandingsWidget />
          </View>

          {/* Coluna da Direita: Destaques e Lideranças */}
          <View style={[styles.column, { flex: 5 }]}>
            <HighlightCard />

            <Text style={styles.sectionTitle}>Líderes (Jogadores) - Médias</Text>
            <View style={styles.leaderboardGrid}>
              <LeaderboardCard entityType="player" seasonId={18} metric="points_per_game" title="Pontos por Jogo" />
              <LeaderboardCard entityType="player" seasonId={18} metric="assists_per_game" title="Assistências" />
              <LeaderboardCard entityType="player" seasonId={18} metric="rebounds_per_game" title="Rebotes" />
              <LeaderboardCard entityType="player" seasonId={18} metric="efficiency_per_game" title="Eficiência" />
              <LeaderboardCard entityType="player" seasonId={18} metric="steals_per_game" title="Roubos de Bola" />
              <LeaderboardCard entityType="player" seasonId={18} metric="blocks_per_game" title="Tocos por Jogo" />
            </View>

            <Text style={styles.sectionTitle}>Líderes (Times) - Médias</Text>
            <View style={styles.leaderboardGrid}>
              <LeaderboardCard entityType="team" seasonId={18} metric="points_per_game" title="Pontos por Jogo" />
              <LeaderboardCard entityType="team" seasonId={18} metric="assists_per_game" title="Assistências" />
              <LeaderboardCard entityType="team" seasonId={18} metric="rebounds_per_game" title="Rebotes" />
              <LeaderboardCard entityType="team" seasonId={18} metric="efficiency_per_game" title="Eficiência" />
              <LeaderboardCard entityType="team" seasonId={18} metric="steals_per_game" title="Roubos de Bola" />
              <LeaderboardCard entityType="team" seasonId={18} metric="blocks_per_game" title="Tocos por Jogo" />
            </View>
          </View>
        </View>
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#0A2E20', // Verde muito escuro premium
    borderWidth: 1,
    borderColor: 'rgba(0, 127, 78, 0.3)',
    borderRadius: 16,
    padding: spacing.xl,
    alignItems: 'center',
    marginBottom: spacing.xl,
    textAlign: 'center',
  },
  bannerTitle: {
    fontSize: typography.fontSize.xl,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  bannerText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: typography.lineHeight.md,
    maxWidth: 700,
    marginBottom: spacing.lg,
  },
  bannerBold: {
    fontFamily: typography.fontFamily.bold,
    color: colors.secondary, // Laranja
  },
  askButton: {
    backgroundColor: colors.secondary, // Laranja
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xxl,
    borderRadius: 8,
    shadowColor: colors.secondary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 3,
  },
  askButtonText: {
    color: colors.textLight,
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
  },
  layoutGrid: {
    flexDirection: 'row',
    width: '100%',
    gap: spacing.lg,
  },
  layoutColumn: {
    flexDirection: 'column',
  },
  column: {
    width: '100%',
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
    marginBottom: spacing.md,
    marginTop: spacing.md,
  },
  leaderboardGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    width: '100%',
  },
});
export default HomeScreen;
