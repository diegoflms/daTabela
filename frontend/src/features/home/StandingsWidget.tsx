import React, { useEffect, useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useAsync } from '../../hooks/useAsync';
import { getStandings } from '../../api/seasons';
import { getTeams } from '../../api/teams';
import { Team } from '../../types/models';
import { FallbackImage } from '../../components/ui/FallbackImage';
import { colors, spacing, typography } from '../../theme';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { Link } from 'expo-router';

export const StandingsWidget: React.FC = () => {
  // Busca a classificação e os times em paralelo
  const { data, loading, error, execute } = useAsync(async () => {
    const [standingsRes, teamsRes] = await Promise.all([
      getStandings(18, 100, 0),
      getTeams(100, 0)
    ]);
    return {
      standings: standingsRes.items || [],
      teams: teamsRes.items || []
    };
  });

  useEffect(() => {
    execute().catch(() => {});
  }, [execute]);

  const teamMap = useMemo(() => {
    const map = new Map<number, Team>();
    if (data?.teams) {
      data.teams.forEach((t) => map.set(t.id, t));
    }
    return map;
  }, [data?.teams]);

  const sortedStandings = useMemo(() => {
    const list = data?.standings || [];
    return [...list].sort((a, b) => (b.wins || 0) - (a.wins || 0));
  }, [data?.standings]);

  if (loading) return <LoadingState message="Carregando classificação..." />;
  if (error) return <ErrorState message={error} onRetry={() => execute()} />;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Tabela NBB</Text>
        <Text style={styles.subtitle}>Classificação Geral</Text>
      </View>

      <View style={styles.table}>
        <View style={styles.tableHeader}>
          <Text style={styles.rankHeaderCell}>#</Text>
          <Text style={[styles.headerCell, styles.teamCell]}>TIMES</Text>
          <Text style={[styles.headerCell, styles.statCell]}>AP(%)</Text>
          <Text style={[styles.headerCell, styles.statCell]}>VIT</Text>
          <Text style={[styles.headerCell, styles.statCell]}>DER</Text>
          <Text style={[styles.headerCell, styles.statCell]}>SAL</Text>
        </View>

        {sortedStandings.length > 0 ? (
          sortedStandings.map((row, idx) => {
            const apVal = row.ap_pct ?? row.pct ?? 0;
            const apText = apVal <= 1 ? (apVal * 100).toFixed(1) : apVal.toFixed(1);
            
            const teamObj = teamMap.get(row.team_id);
            const teamName = teamObj?.canonical_name || row.team_name || 'Sem nome';
            const teamLogo = teamObj?.logo_url || null;

            return (
              <Link key={`standing-${row.id || idx}`} href={`/teams/${row.team_id}` as any} asChild>
                <TouchableOpacity 
                  style={StyleSheet.flatten([styles.row, idx % 2 === 1 && styles.rowAlternate])}
                  activeOpacity={0.7}
                >
                  <Text style={styles.rankText}>{idx + 1}</Text>
                  <View style={[styles.teamCell, styles.teamRow]}>
                    <FallbackImage
                      sourceUrl={teamLogo}
                      textFallback={teamName}
                      type="team"
                      size={24}
                      style={styles.smallLogo}
                    />
                    <Text style={[styles.cell, styles.teamNameText]} numberOfLines={1}>
                      {teamName}
                    </Text>
                  </View>
                  <Text style={[styles.cell, styles.statCell]}>
                    {apText}%
                  </Text>
                  <Text style={[styles.cell, styles.statCell, styles.winText]}>{row.wins}</Text>
                  <Text style={[styles.cell, styles.statCell, styles.lossText]}>{row.losses}</Text>
                  <Text style={[styles.cell, styles.statCell, styles.diffText]}>
                    {row.point_diff !== undefined ? (row.point_diff > 0 ? `+${row.point_diff}` : row.point_diff) : '0'}
                  </Text>
                </TouchableOpacity>
              </Link>
            );
          })
        ) : (

          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Sem dados de classificação.</Text>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    width: '100%',
  },
  header: {
    marginBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: spacing.sm,
  },
  title: {
    fontSize: typography.fontSize.lg,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
  },
  subtitle: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: 2,
  },
  table: {
    width: '100%',
  },
  tableHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.secondary,
    borderRadius: 6,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.sm,
    marginBottom: spacing.xs,
  },
  rankHeaderCell: {
    width: 24,
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textAlign: 'center',
    marginRight: spacing.xs,
  },
  headerCell: {
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.surface,
  },
  rowAlternate: {
    backgroundColor: '#252525',
  },
  rankText: {
    width: 24,
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.medium,
    textAlign: 'center',
    marginRight: spacing.xs,
  },
  cell: {
    fontSize: typography.fontSize.sm,
    color: colors.text,
  },
  teamCell: {
    flex: 2,
    paddingLeft: spacing.xs,
  },
  teamRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  smallLogo: {
    borderRadius: 4,
  },
  teamNameText: {
    fontFamily: typography.fontFamily.medium,
    flex: 1,
  },
  statCell: {
    width: 48,
    textAlign: 'center',
  },
  winText: {
    fontFamily: typography.fontFamily.bold,
    color: colors.text, // Manteve branco para sobriedade, ou verde
  },
  lossText: {
    color: colors.textSecondary,
  },
  diffText: {
    fontFamily: typography.fontFamily.medium,
    color: colors.textSecondary,
  },
  emptyContainer: {
    padding: spacing.lg,
    alignItems: 'center',
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: typography.fontSize.sm,
  },
});
export default StandingsWidget;
