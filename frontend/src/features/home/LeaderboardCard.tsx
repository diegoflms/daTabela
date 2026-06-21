import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useAsync } from '../../hooks/useAsync';
import { getPlayerRanking, getTeamRanking } from '../../api/rankings';
import { colors, spacing, typography } from '../../theme';
import { formatCellValue } from '../../utils/formatters';
import { Link } from 'expo-router';

interface LeaderboardCardProps {
  metric: string;
  title: string;
  unit?: string;
  entityType?: 'player' | 'team';
  seasonId?: number;
  teamId?: number;
}

export const LeaderboardCard: React.FC<LeaderboardCardProps> = ({
  metric,
  title,
  unit = '',
  entityType = 'player',
  seasonId,
  teamId,
}) => {
  const { data, loading, error, execute } = useAsync(() => {
    return entityType === 'team'
      ? getTeamRanking(metric, seasonId)
      : getPlayerRanking(metric, seasonId, teamId);
  });

  useEffect(() => {
    execute().catch(() => {});
  }, [execute, metric, seasonId, entityType, teamId]);

  const items = (data as any)?.items || [];
  const leader = items[0];
  const runnersUp = items.slice(1, 3); // 2º e 3º colocados

  const displayName = leader
    ? (entityType === 'team' ? (leader.team_name || 'Time') : (leader.player_name || 'Jogador'))
    : '';

  const subText = leader
    ? (entityType === 'team' ? 'NBB' : (leader.team_name || '-'))
    : '';

  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator color={colors.primary} size="small" />
        </View>
      ) : error ? (
        <Text style={styles.errorText}>Indisponível</Text>
      ) : leader ? (
        <View style={styles.content}>
          {/* Top 1 */}
          <View style={styles.leaderContainer}>
            <View style={styles.leaderInfo}>
              {entityType === 'team' ? (
                <Link href={`/teams/${leader.team_id}` as any} asChild>
                  <TouchableOpacity activeOpacity={0.7}>
                    <Text style={styles.leaderName} numberOfLines={1}>
                      {displayName}
                    </Text>
                  </TouchableOpacity>
                </Link>
              ) : (
                <Link href={`/players/${leader.player_id}` as any} asChild>
                  <TouchableOpacity activeOpacity={0.7}>
                    <Text style={styles.leaderName} numberOfLines={1}>
                      {displayName}
                    </Text>
                  </TouchableOpacity>
                </Link>
              )}

              {entityType === 'team' ? (
                <Text style={styles.leaderTeam} numberOfLines={1}>
                  {subText}
                </Text>
              ) : (
                <Link href={`/teams/${leader.team_id}` as any} asChild>
                  <TouchableOpacity activeOpacity={0.7}>
                    <Text style={styles.leaderTeam} numberOfLines={1}>
                      {subText}
                    </Text>
                  </TouchableOpacity>
                </Link>
              )}
            </View>
            <View style={styles.leaderValueContainer}>
              <Text style={styles.leaderValue}>
                {formatCellValue(leader.ranking_value, metric)}
              </Text>
              {unit !== '' && <Text style={styles.unit}>{unit}</Text>}
            </View>
          </View>

          {/* Runners-up (2º e 3º) */}
          {runnersUp.length > 0 && (
            <View style={styles.runnersList}>
              {runnersUp.map((item: any, idx: number) => {
                const runnerName = entityType === 'team'
                  ? (item.team_name || 'Time')
                  : (item.player_name || 'Jogador');
                
                const runnerLink = entityType === 'team'
                  ? `/teams/${item.team_id}`
                  : `/players/${item.player_id}`;

                return (
                  <View key={`runner-${idx}-${item.id || item.player_id || idx}`} style={styles.runnerRow}>
                    <Text style={styles.runnerRank}>{idx + 2}</Text>
                    <Link href={runnerLink as any} asChild>
                      <TouchableOpacity activeOpacity={0.7} style={styles.runnerNameTouchable}>
                        <View style={{ flexDirection: 'column', flex: 1 }}>
                          <Text style={styles.runnerName} numberOfLines={1}>
                            {runnerName}
                          </Text>
                          {entityType === 'player' && item.team_name && (
                            <Text style={styles.runnerTeam} numberOfLines={1}>
                              {item.team_name}
                            </Text>
                          )}
                        </View>
                      </TouchableOpacity>
                    </Link>
                    <Text style={styles.runnerValue}>
                      {formatCellValue(item.ranking_value, metric)}
                    </Text>
                  </View>
                );
              })}
            </View>
          )}
        </View>
      ) : (
        <Text style={styles.emptyText}>Sem dados</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: spacing.md,
    flex: 1,
    minWidth: 200,
    margin: spacing.xs,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  title: {
    fontSize: 11,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: spacing.xs,
    marginBottom: spacing.sm,
  },
  loadingContainer: {
    height: 80,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorText: {
    fontSize: typography.fontSize.sm,
    color: colors.error,
    textAlign: 'center',
    paddingVertical: spacing.md,
  },
  emptyText: {
    fontSize: typography.fontSize.sm,
    color: colors.textMuted,
    textAlign: 'center',
    paddingVertical: spacing.md,
  },
  content: {
    width: '100%',
  },
  leaderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  leaderInfo: {
    flex: 1,
    marginRight: spacing.xs,
  },
  leaderName: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
  },
  leaderTeam: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: 2,
  },
  leaderValueContainer: {
    alignItems: 'flex-end',
  },
  leaderValue: {
    fontSize: 26,
    fontFamily: typography.fontFamily.bold,
    color: colors.accent, // Dourado/Amarelo como protótipo
  },
  unit: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  runnersList: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.sm,
  },
  runnerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: spacing.sm,
    backgroundColor: '#2A2A2A', // Visual metálico escuro
    borderRadius: 6,
    marginVertical: 2,
  },
  runnerRank: {
    width: 14,
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.bold,
  },
  runnerNameTouchable: {
    flex: 1,
  },
  runnerName: {
    fontSize: typography.fontSize.xs,
    color: colors.text,
    paddingHorizontal: spacing.xs,
  },
  runnerTeam: {
    fontSize: 9,
    color: colors.textSecondary,
    paddingHorizontal: spacing.xs,
    marginTop: 1,
  },
  runnerValue: {
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
  },
});
export default LeaderboardCard;
