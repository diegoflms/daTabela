import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { useAsync } from '../../hooks/useAsync';
import { getGames } from '../../api/games';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { EmptyState } from '../../components/ui/EmptyState';
import { colors, spacing, typography } from '../../theme';
import { formatShortDate } from '../../utils/formatters';
import { Link } from 'expo-router';

export const GamesScreen: React.FC = () => {
  const { data, loading, error, execute } = useAsync(() => getGames(50, 0));

  useEffect(() => {
    execute().catch(() => {});
  }, [execute]);

  const games = data?.items || [];

  return (
    <AppShell>
      <PageContainer>
        <View style={styles.header}>
          <Text style={styles.title}>Partidas do NBB</Text>
          <Text style={styles.subtitle}>
            Acompanhe o placar dos confrontos e veja estatísticas detalhadas de cada jogo.
          </Text>
        </View>

        {loading && <LoadingState message="Carregando partidas..." />}

        {error && !loading && (
          <ErrorState message={error} onRetry={() => execute()} />
        )}

        {!loading && !error && (
          <View style={styles.listContainer}>
            {games.length > 0 ? (
              <View style={styles.list}>
                {games.map((game, idx) => (
                  <Link key={`game-row-${game.id || idx}`} href={`/games/${game.id}` as any} asChild>
                    <TouchableOpacity style={styles.row} activeOpacity={0.8}>
                      <View style={styles.dateContainer}>
                        <Text style={styles.dateText}>
                          {formatShortDate(game.game_date || game.date)}
                        </Text>
                        <Text style={styles.stageText}>
                          {game.phase || game.stage || 'NBB'}
                        </Text>
                      </View>

                      <View style={styles.teamsContainer}>
                        <View style={styles.teamLine}>
                          <Text style={[styles.teamName, Number(game.home_score || 0) > Number(game.away_score || 0) && styles.winner]}>
                            {game.home_team_name}
                          </Text>
                          <Text style={[styles.score, Number(game.home_score || 0) > Number(game.away_score || 0) && styles.winner]}>
                            {game.home_score}
                          </Text>
                        </View>
                        <View style={styles.teamLine}>
                          <Text style={[styles.teamName, Number(game.away_score || 0) > Number(game.home_score || 0) && styles.winner]}>
                            {game.away_team_name}
                          </Text>
                          <Text style={[styles.score, Number(game.away_score || 0) > Number(game.home_score || 0) && styles.winner]}>
                            {game.away_score}
                          </Text>
                        </View>
                      </View>

                      <Text style={styles.arrow}>➔</Text>
                    </TouchableOpacity>
                  </Link>
                ))}
              </View>
            ) : (
              <EmptyState message="Nenhuma partida encontrada." />
            )}
          </View>
        )}
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  header: {
    marginBottom: spacing.lg,
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontFamily: typography.fontFamily.bold,
    color: colors.primaryDark,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  listContainer: {
    width: '100%',
    marginVertical: spacing.md,
  },
  list: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    backgroundColor: colors.surface,
    overflow: 'hidden',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  dateContainer: {
    width: 100,
    marginRight: spacing.md,
  },
  dateText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
  },
  stageText: {
    fontSize: typography.fontSize.xs,
    color: colors.textMuted,
    marginTop: 2,
    textTransform: 'uppercase',
  },
  teamsContainer: {
    flex: 1,
    gap: 4,
  },
  teamLine: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  teamName: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.regular,
  },
  score: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.medium,
    marginRight: spacing.lg,
  },
  winner: {
    color: colors.text,
    fontFamily: typography.fontFamily.bold,
  },
  arrow: {
    color: colors.textMuted,
    fontSize: typography.fontSize.md,
  },
});
export default GamesScreen;
