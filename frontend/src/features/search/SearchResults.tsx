import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { GlobalSearchResponse } from '../../types/api';
import { colors, spacing, typography } from '../../theme';
import { FallbackImage } from '../../components/ui/FallbackImage';
import { Link } from 'expo-router';
import { formatShortDate } from '../../utils/formatters';

interface SearchResultsProps {
  results: GlobalSearchResponse | null;
  query: string;
}

export const SearchResults: React.FC<SearchResultsProps> = ({ results, query }) => {
  if (!results) return null;

  const { players = [], teams = [], games = [] } = results;
  const totalResults = players.length + teams.length + games.length;

  if (totalResults === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>
          Nenhum jogador, time ou partida encontrado para "{query}".
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.summaryText}>
        Encontramos {totalResults} resultado(s) para sua busca:
      </Text>

      {/* Players */}
      {players.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Jogadores ({players.length})</Text>
          <View style={styles.list}>
            {players.map((player) => (
              <Link key={`search-player-${player.id}`} href={`/players/${player.id}` as any} asChild>
                <TouchableOpacity style={styles.itemRow} activeOpacity={0.7}>
                  <FallbackImage
                    textFallback={player.name}
                    type="player"
                    size={40}
                    style={styles.itemAvatar}
                  />
                  <View style={styles.itemInfo}>
                    <Text style={styles.itemName}>{player.name}</Text>
                    <Text style={styles.itemSub}>{player.position || 'Jogador'} • {player.birthplace || 'NBB'}</Text>
                  </View>
                  <Text style={styles.arrow}>➔</Text>
                </TouchableOpacity>
              </Link>
            ))}
          </View>
        </View>
      )}

      {/* Teams */}
      {teams.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Times ({teams.length})</Text>
          <View style={styles.list}>
            {teams.map((team) => (
              <Link key={`search-team-${team.id}`} href={`/teams/${team.id}` as any} asChild>
                <TouchableOpacity style={styles.itemRow} activeOpacity={0.7}>
                  <FallbackImage
                    textFallback={team.name}
                    type="team"
                    size={40}
                    style={styles.itemAvatar}
                  />
                  <View style={styles.itemInfo}>
                    <Text style={styles.itemName}>{team.name}</Text>
                    <Text style={styles.itemSub}>{team.city || 'Cidade'} / {team.state || 'UF'}</Text>
                  </View>
                  <Text style={styles.arrow}>➔</Text>
                </TouchableOpacity>
              </Link>
            ))}
          </View>
        </View>
      )}

      {/* Games */}
      {games.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Partidas ({games.length})</Text>
          <View style={styles.list}>
            {games.map((game) => (
              <Link key={`search-game-${game.id}`} href={`/games/${game.id}` as any} asChild>
                <TouchableOpacity style={styles.itemRow} activeOpacity={0.7}>
                  <View style={styles.itemInfo}>
                    <Text style={styles.itemName}>
                      {game.home_team_name} {game.home_score} x {game.away_score} {game.away_team_name}
                    </Text>
                    <Text style={styles.itemSub}>
                      {formatShortDate(game.game_date || game.date)} • {game.arena || game.venue || 'Arena'}
                    </Text>
                  </View>
                  <Text style={styles.arrow}>➔</Text>
                </TouchableOpacity>
              </Link>
            ))}
          </View>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    width: '100%',
  },
  summaryText: {
    fontSize: typography.fontSize.sm,
    color: colors.textMuted,
    marginBottom: spacing.md,
    fontFamily: typography.fontFamily.medium,
  },
  section: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  list: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    backgroundColor: colors.surface,
    overflow: 'hidden',
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  itemAvatar: {
    marginRight: spacing.md,
  },
  itemInfo: {
    flex: 1,
  },
  itemName: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
  },
  itemSub: {
    fontSize: typography.fontSize.xs,
    color: colors.textMuted,
    marginTop: 2,
  },
  arrow: {
    fontSize: typography.fontSize.sm,
    color: colors.textMuted,
    marginLeft: spacing.sm,
  },
  emptyContainer: {
    padding: spacing.xxl,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
    fontFamily: typography.fontFamily.medium,
  },
});
export default SearchResults;
