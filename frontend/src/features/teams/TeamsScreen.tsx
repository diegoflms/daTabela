import React, { useEffect, useState, useMemo } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { TeamCard } from './TeamCard';
import { useAsync } from '../../hooks/useAsync';
import { getTeams } from '../../api/teams';
import { getSeasons } from '../../api/seasons';
import { Select } from '../../components/ui/Select';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { EmptyState } from '../../components/ui/EmptyState';
import { colors, spacing, typography } from '../../theme';

export const TeamsScreen: React.FC = () => {
  const [selectedSeasonId, setSelectedSeasonId] = useState<string | number>(18);

  const { data: teamsData, loading: loadingTeams, error: errorTeams, execute: fetchTeams } = useAsync(() => getTeams(100, 0));
  const { data: seasonsData, execute: fetchSeasons } = useAsync(() => getSeasons(50, 0));

  useEffect(() => {
    fetchTeams().catch(() => {});
    fetchSeasons().catch(() => {});
  }, [fetchTeams, fetchSeasons]);

  const teams = teamsData?.items || [];
  const seasonsList = seasonsData?.items || [];

  const seasonOptions = useMemo(() => {
    return [
      { label: 'Todas as Temporadas', value: '' },
      ...seasonsList.map((s) => ({
        label: s.name,
        value: s.id,
      })),
    ];
  }, [seasonsList]);

  const filteredTeams = useMemo(() => {
    if (selectedSeasonId === '') return teams;
    const seasonVal = Number(selectedSeasonId);
    return teams.filter((t) => {
      const first = t.first_seen_season_id || 1;
      const last = t.last_seen_season_id || 18;
      return first <= seasonVal && seasonVal <= last;
    });
  }, [teams, selectedSeasonId]);

  const handleRetry = () => {
    fetchTeams().catch(() => {});
    fetchSeasons().catch(() => {});
  };

  return (
    <AppShell>
      <PageContainer>
        <View style={styles.header}>
          <Text style={styles.title}>Times</Text>
          <View style={styles.filterRow}>
            <Select
              selectedValue={selectedSeasonId}
              onValueChange={setSelectedSeasonId}
              options={seasonOptions}
              placeholder="Filtrar por Temporada"
              variant="orange"
            />
          </View>
        </View>

        {loadingTeams && <LoadingState message="Carregando equipes..." />}

        {errorTeams && !loadingTeams && (
          <ErrorState message={errorTeams} onRetry={handleRetry} />
        )}

        {!loadingTeams && !errorTeams && (
          <View style={styles.resultsContainer}>
            {filteredTeams.length > 0 ? (
              <View style={styles.grid}>
                {filteredTeams.map((team) => (
                  <TeamCard key={`team-card-${team.id}`} team={team} />
                ))}
              </View>
            ) : (
              <EmptyState message="Nenhuma equipe cadastrada para a temporada selecionada." />
            )}
          </View>
        )}
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  header: {
    marginBottom: spacing.xl,
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  title: {
    fontSize: 32,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textAlign: 'center',
    marginTop: spacing.md,
  },
  filterRow: {
    width: '100%',
    maxWidth: 320,
    marginTop: spacing.md,
  },
  resultsContainer: {
    width: '100%',
    marginVertical: spacing.md,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.lg,
    justifyContent: 'center',
    width: '100%',
  },
});
export default TeamsScreen;
