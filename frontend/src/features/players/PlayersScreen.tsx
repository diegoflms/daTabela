import React, { useState, useEffect, useMemo } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { PlayerFilters } from './PlayerFilters';
import { PlayerCard } from './PlayerCard';
import { useAsync } from '../../hooks/useAsync';
import { getPlayers } from '../../api/players';
import { getTeams } from '../../api/teams';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { EmptyState } from '../../components/ui/EmptyState';
import { colors, spacing, typography } from '../../theme';

export const PlayersScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTeam, setSelectedTeam] = useState<string | number>('');

  // Busca lista de jogadores (aumentamos o limite para termos mais dados locais para filtrar)
  const { data: playersData, loading: loadingPlayers, error: errorPlayers, execute: fetchPlayers } = useAsync(
    () => getPlayers(searchQuery, 1000, 0)
  );

  // Busca lista de times para carregar no dropdown de filtros
  const { data: teamsData, execute: fetchTeams } = useAsync(() => getTeams(100, 0));

  useEffect(() => {
    fetchPlayers().catch(() => {});
    fetchTeams().catch(() => {});
  }, [fetchPlayers, fetchTeams]);

  // Refaz a busca na API quando a query de busca muda (debounce simples via botão ou na mudança)
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchPlayers().catch(() => {});
    }, 400); // Debounce de 400ms para evitar chamadas excessivas
    return () => clearTimeout(timer);
  }, [searchQuery, fetchPlayers]);

  const teamOptions = useMemo(() => {
    const items = teamsData?.items || [];
    // Filtra apenas os times ativos (last_seen_season_id >= 18)
    const activeTeams = items.filter(t => (t.last_seen_season_id || 0) >= 18);
    return [
      { label: 'Todos os Times', value: '' },
      ...activeTeams.map((team) => ({
        label: team.canonical_name || team.name,
        value: team.id,
      })),
    ];
  }, [teamsData]);

  // Filtra os jogadores localmente por time
  const filteredPlayers = useMemo(() => {
    let items = playersData?.items || [];

    if (selectedTeam !== '') {
      items = items.filter((p) => p.current_team_id === Number(selectedTeam));
    }

    return items;
  }, [playersData, selectedTeam]);

  const handleRetry = () => {
    fetchPlayers().catch(() => {});
    fetchTeams().catch(() => {});
  };

  return (
    <AppShell>
      <PageContainer>
        <View style={styles.header}>
          <Text style={styles.title}>Jogadores</Text>
        </View>

        <PlayerFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedTeam={selectedTeam}
          onTeamChange={setSelectedTeam}
          teamOptions={teamOptions}
        />

        {loadingPlayers && <LoadingState message="Carregando jogadores..." />}

        {errorPlayers && !loadingPlayers && (
          <ErrorState message={errorPlayers} onRetry={handleRetry} />
        )}

        {!loadingPlayers && !errorPlayers && (
          <View style={styles.resultsContainer}>
            {filteredPlayers.length > 0 ? (
              <View style={styles.grid}>
                {filteredPlayers.map((player) => (
                  <PlayerCard key={`player-card-${player.id}`} player={player} />
                ))}
              </View>
            ) : (
              <EmptyState message="Nenhum jogador encontrado com os filtros selecionados." />
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
  resultsContainer: {
    width: '100%',
    marginVertical: spacing.md,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
    justifyContent: 'center',
    width: '100%',
  },
});
export default PlayersScreen;
