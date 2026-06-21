import React, { useState, useEffect, useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { Select } from '../../components/ui/Select';
import { RankingTable } from './RankingTable';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { useAsync } from '../../hooks/useAsync';
import {
  getPlayerRankingMetrics,
  getPlayerRanking,
  getTeamRankingMetrics,
  getTeamRanking,
} from '../../api/rankings';
import { colors, spacing, typography } from '../../theme';
import { formatColumnLabel } from '../../utils/labels';

export const RankingsScreen: React.FC = () => {
  const [type, setType] = useState<'players' | 'teams'>('players');
  const [selectedMetric, setSelectedMetric] = useState<string>('');

  // Busca as métricas disponíveis dependendo do tipo selecionado
  const { 
    data: playerMetricsData, 
    loading: loadingPM, 
    execute: fetchPlayerMetrics 
  } = useAsync(getPlayerRankingMetrics);

  const { 
    data: teamMetricsData, 
    loading: loadingTM, 
    execute: fetchTeamMetrics 
  } = useAsync(getTeamRankingMetrics);

  // Busca a tabela de ranking
  const { 
    data: rankingData, 
    loading: loadingRanking, 
    error: errorRanking, 
    execute: fetchRanking 
  } = useAsync((metric: string) => 
    type === 'players' ? getPlayerRanking(metric) : getTeamRanking(metric)
  );

  // Carrega as métricas iniciais
  useEffect(() => {
    fetchPlayerMetrics().catch(() => {});
    fetchTeamMetrics().catch(() => {});
  }, [fetchPlayerMetrics, fetchTeamMetrics]);

  // Define a métrica padrão quando as métricas mudam ou quando o tipo muda
  const currentMetrics = useMemo(() => {
    return type === 'players' 
      ? playerMetricsData?.metrics || [] 
      : teamMetricsData?.metrics || [];
  }, [type, playerMetricsData, teamMetricsData]);

  useEffect(() => {
    if (currentMetrics.length > 0) {
      // Se a métrica selecionada anteriormente não existe na nova lista de métricas, use a primeira
      if (!currentMetrics.includes(selectedMetric)) {
        setSelectedMetric(currentMetrics[0]);
      }
    } else {
      setSelectedMetric('');
    }
  }, [currentMetrics, selectedMetric]);

  // Dispara a busca do ranking de fato quando a métrica selecionada muda
  useEffect(() => {
    if (selectedMetric) {
      fetchRanking(selectedMetric).catch(() => {});
    }
  }, [selectedMetric, fetchRanking, type]);

  const selectOptions = useMemo(() => {
    return currentMetrics.map((m) => ({
      label: formatColumnLabel(m),
      value: m,
    }));
  }, [currentMetrics]);

  const handleTypeChange = (newType: 'players' | 'teams') => {
    setType(newType);
  };

  const rankingItems = rankingData?.items || [];

  return (
    <AppShell>
      <PageContainer>
        <View style={styles.header}>
          <Text style={styles.title}>Líderes e Rankings</Text>
          <Text style={styles.subtitle}>
            Acompanhe o ranking completo de jogadores e times por diferentes métricas estatísticas.
          </Text>
        </View>

        {/* Tipo de Ranking (Jogadores / Times) */}
        <View style={styles.tabRow}>
          <TouchableOpacity
            style={[styles.tab, type === 'players' && styles.activeTab]}
            onPress={() => handleTypeChange('players')}
            activeOpacity={0.7}
          >
            <Text style={[styles.tabText, type === 'players' && styles.activeTabText]}>
              Rankings de Jogadores
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, type === 'teams' && styles.activeTab]}
            onPress={() => handleTypeChange('teams')}
            activeOpacity={0.7}
          >
            <Text style={[styles.tabText, type === 'teams' && styles.activeTabText]}>
              Rankings de Equipes
            </Text>
          </TouchableOpacity>
        </View>

        {/* Selector de Métrica */}
        <View style={styles.filterRow}>
          <Text style={styles.filterLabel}>Métrica:</Text>
          {selectOptions.length > 0 ? (
            <Select
              selectedValue={selectedMetric}
              onValueChange={setSelectedMetric}
              options={selectOptions}
              placeholder="Escolha a métrica..."
            />
          ) : (
            <ActivityIndicator size="small" color={colors.primary} />
          )}
        </View>

        {/* Exibição da tabela */}
        {loadingRanking ? (
          <LoadingState message="Calculando ranking..." />
        ) : errorRanking ? (
          <ErrorState message={errorRanking} onRetry={() => fetchRanking(selectedMetric)} />
        ) : rankingItems.length > 0 ? (
          <View style={styles.rankingBox}>
            <Text style={styles.rankingTitle}>
              Top {rankingItems.length} por {formatColumnLabel(selectedMetric)}
            </Text>
            <RankingTable items={rankingItems} metricKey={selectedMetric} type={type} />
          </View>
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Escolha uma métrica para visualizar o ranking.</Text>
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
  tabRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    marginBottom: spacing.lg,
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
  filterRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    marginBottom: spacing.lg,
    width: '100%',
    maxWidth: 400,
  },
  filterLabel: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
  },
  rankingBox: {
    width: '100%',
  },
  rankingTitle: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  emptyContainer: {
    padding: spacing.xxl,
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: typography.fontSize.md,
  },
});
export default RankingsScreen;
