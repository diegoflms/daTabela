import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { StatsTable } from '../../components/data/StatsTable';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { colors, spacing, typography } from '../../theme';
import { getGame, getGamePlayerStats, getGameTeamStats } from '../../api/games';
import { useAsync } from '../../hooks/useAsync';
import { formatShortDate } from '../../utils/formatters';

interface GameDetailScreenProps {
  id: number;
}

export const GameDetailScreen: React.FC<GameDetailScreenProps> = ({ id }) => {
  const [activeTab, setActiveTab] = useState<'players' | 'teams'>('players');

  const { data: game, loading: loadingGame, error: errorGame, execute: fetchGame } = useAsync(() => getGame(id));
  const { data: playerStats, loading: loadingPlayers, execute: fetchPlayerStats } = useAsync(() => getGamePlayerStats(id));
  const { data: teamStats, loading: loadingTeams, execute: fetchTeamStats } = useAsync(() => getGameTeamStats(id));

  useEffect(() => {
    if (id) {
      fetchGame().catch(() => {});
      fetchPlayerStats().catch(() => {});
      fetchTeamStats().catch(() => {});
    }
  }, [id, fetchGame, fetchPlayerStats, fetchTeamStats]);

  if (loadingGame) return <LoadingState message="Carregando detalhes da partida..." />;
  
  if (errorGame || !game) {
    return (
      <AppShell>
        <PageContainer>
          <ErrorState
            message={errorGame || 'Partida não encontrada no banco SQLite.'}
            onRetry={() => fetchGame()}
          />
        </PageContainer>
      </AppShell>
    );
  }

  const pStatsList = playerStats?.items || playerStats || [];
  const tStatsList = teamStats?.items || teamStats || [];

  return (
    <AppShell>
      <PageContainer>
        {/* Placar de Jogo */}
        <View style={styles.scoreboard}>
          <View style={styles.dateRow}>
            <Text style={styles.dateText}>{formatShortDate(game.game_date || game.date)}</Text>
            {game.round && <Text style={styles.roundText}>Rodada {game.round}</Text>}
          </View>

          <View style={styles.scoresRow}>
            <View style={styles.teamScoreBox}>
              <Text style={[styles.teamName, Number(game.home_score || 0) > Number(game.away_score || 0) && styles.winnerText]}>
                {game.home_team_name}
              </Text>
              <Text style={[styles.teamScore, Number(game.home_score || 0) > Number(game.away_score || 0) && styles.winnerText]}>
                {game.home_score}
              </Text>
            </View>

            <Text style={styles.versusText}>vs</Text>

            <View style={styles.teamScoreBox}>
              <Text style={[styles.teamScore, Number(game.away_score || 0) > Number(game.home_score || 0) && styles.winnerText]}>
                {game.away_score}
              </Text>
              <Text style={[styles.teamName, Number(game.away_score || 0) > Number(game.home_score || 0) && styles.winnerText]}>
                {game.away_team_name}
              </Text>
            </View>
          </View>

          {(game.arena || game.venue || game.city) && (
            <View style={styles.arenaRow}>
              <Text style={styles.arenaText}>
                📍 {game.arena || game.venue || 'Arena'}{game.city ? ` - ${game.city}` : ''}{game.state ? `, ${game.state}` : ''}
              </Text>
            </View>
          )}
        </View>

        {/* Abas e Estatísticas da Partida */}
        <View style={styles.statsContainer}>
          <View style={styles.tabRow}>
            <TouchableOpacity
              style={[styles.tab, activeTab === 'players' && styles.activeTab]}
              onPress={() => setActiveTab('players')}
              activeOpacity={0.7}
            >
              <Text style={[styles.tabText, activeTab === 'players' && styles.activeTabText]}>
                Estatísticas de Jogadores
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.tab, activeTab === 'teams' && styles.activeTab]}
              onPress={() => setActiveTab('teams')}
              activeOpacity={0.7}
            >
              <Text style={[styles.tabText, activeTab === 'teams' && styles.activeTabText]}>
                Estatísticas de Equipes
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.tabContent}>
            {activeTab === 'players' ? (
              loadingPlayers ? (
                <LoadingState message="Carregando estatísticas dos atletas..." />
              ) : pStatsList.length > 0 ? (
                <StatsTable data={pStatsList} />
              ) : (
                <Text style={styles.noDataText}>Nenhuma estatística de jogador registrada para esta partida.</Text>
              )
            ) : loadingTeams ? (
              <LoadingState message="Carregando estatísticas das equipes..." />
            ) : tStatsList.length > 0 ? (
              <StatsTable data={tStatsList} />
            ) : (
              <Text style={styles.noDataText}>Nenhuma estatística de equipe registrada para esta partida.</Text>
            )}
          </View>
        </View>
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  scoreboard: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    alignItems: 'center',
    marginBottom: spacing.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
    width: '100%',
  },
  dateRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  dateText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
  },
  roundText: {
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    backgroundColor: colors.textMuted,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: 12,
  },
  scoresRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    marginVertical: spacing.sm,
  },
  teamScoreBox: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
  },
  teamName: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
    color: colors.textSecondary,
    flex: 1,
  },
  teamScore: {
    fontSize: typography.fontSize.xxl,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    marginHorizontal: spacing.md,
  },
  versusText: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.textMuted,
  },
  winnerText: {
    color: colors.text,
    fontFamily: typography.fontFamily.bold,
  },
  arenaRow: {
    marginTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.sm,
    width: '100%',
    alignItems: 'center',
  },
  arenaText: {
    fontSize: typography.fontSize.xs,
    color: colors.textMuted,
    fontFamily: typography.fontFamily.medium,
  },
  statsContainer: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    width: '100%',
  },
  tabRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    marginBottom: spacing.md,
  },
  tab: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: colors.primary,
  },
  tabText: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
    color: colors.textSecondary,
  },
  activeTabText: {
    color: colors.primary,
    fontFamily: typography.fontFamily.bold,
  },
  tabContent: {
    width: '100%',
  },
  noDataText: {
    fontSize: typography.fontSize.sm,
    color: colors.textMuted,
    textAlign: 'center',
    padding: spacing.xl,
  },
});
export default GameDetailScreen;
