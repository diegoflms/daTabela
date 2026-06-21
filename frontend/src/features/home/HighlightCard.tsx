import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useAsync } from '../../hooks/useAsync';
import { getGames, getGamePlayerStats } from '../../api/games';
import { getPlayer } from '../../api/players';
import { FallbackImage } from '../../components/ui/FallbackImage';
import { colors, spacing, typography } from '../../theme';
import { Link } from 'expo-router';

export const HighlightCard: React.FC = () => {
  const { data: highlight, loading, error, execute } = useAsync(async () => {
    // 1. Busca o último jogo (offset = 0 já que a API retorna ordenado por data decrescente)
    const lastGameRes = await getGames(1, 0);
    const lastGame = lastGameRes.items?.[0];
    if (!lastGame) return null;

    // 3. Busca estatísticas dos jogadores nessa partida
    const statsRes = await getGamePlayerStats(lastGame.id);
    const statsList = statsRes.items || [];
    if (statsList.length === 0) return null;

    // 4. Ordena por eficiência DESC e pontos DESC para achar o destaque
    const sortedStats = [...statsList].sort((a, b) => {
      const effA = Number(a.efficiency || 0);
      const effB = Number(b.efficiency || 0);
      if (effB !== effA) return effB - effA;
      return Number(b.points || 0) - Number(a.points || 0);
    });

    const topStat = sortedStats[0];
    if (!topStat) return null;

    // 5. Busca detalhes do jogador destaque (que inclui o JOIN com time atual e logo)
    const playerDetails = await getPlayer(topStat.player_id);

    // Formata a linha de estatísticas
    const minutes = topStat.minutes_decimal || topStat.minutes_text || '0';
    const minVal = typeof minutes === 'number' ? minutes.toFixed(1) : parseFloat(minutes).toFixed(1);
    
    const statsLine = `${minVal} MIN • ${Number(topStat.points || 0).toFixed(1)} PTS • ${Number(topStat.total_rebounds || 0).toFixed(1)} REB • ${Number(topStat.assists || 0).toFixed(1)} AST • ${Number(topStat.turnovers || 0).toFixed(1)} ER • ${Number(topStat.steals || 0).toFixed(1)} BR • ${Number(topStat.blocks || 0).toFixed(1)} TO`;

    return {
      player: playerDetails,
      statsLine,
      game: lastGame,
      topStat
    };
  });

  useEffect(() => {
    execute().catch(() => {});
  }, [execute]);

  if (loading) {
    return (
      <View style={[styles.card, styles.loadingCard]}>
        <ActivityIndicator color={colors.primary} size="large" />
        <Text style={styles.loadingText}>Buscando destaque do último jogo...</Text>
      </View>
    );
  }

  if (error || !highlight || !highlight.player) {
    // Fallback estático caso falhe
    return (
      <Link href="/players/854" asChild>
        <TouchableOpacity style={styles.card} activeOpacity={0.9}>
          <View style={styles.contentRow}>
            <View style={styles.leftContent}>
              <Text style={styles.headerTitle}>Destaque do dia</Text>
              <Text style={styles.name}>#854 Lucas Dias</Text>
              <Text style={styles.statsLine}>
                26.0 MIN • 22.0 PTS • 5.0 REB • 2.0 AST • 1.0 ER • 1.0 BR • 1.0 TO
              </Text>
            </View>
            <View style={styles.rightContent}>
              <FallbackImage
                textFallback="FRA"
                type="team"
                size={72}
                style={styles.teamLogo}
              />
            </View>
          </View>
        </TouchableOpacity>
      </Link>
    );
  }

  const { player, statsLine } = highlight;
  const displayName = player.display_name || player.full_name || 'Jogador';
  const jersey = player.profile_jersey_number !== undefined ? `#${player.profile_jersey_number} ` : '';

  return (
    <Link href={`/players/${player.id}` as any} asChild>
      <TouchableOpacity style={styles.card} activeOpacity={0.9}>
        <View style={styles.contentRow}>
          {/* Lado Esquerdo: Foto e Textos */}
          <View style={styles.leftInfoBlock}>
            <FallbackImage
              sourceUrl={player.photo_url}
              textFallback={displayName}
              type="player"
              size={80}
              style={styles.playerAvatar}
            />
            <View style={styles.leftContent}>
              <Text style={styles.headerTitle}>Destaque do dia (Último jogo)</Text>
              <Text style={styles.name} numberOfLines={1}>
                {jersey}{displayName}
              </Text>
              <Text style={styles.statsLine}>{statsLine}</Text>
            </View>
          </View>

          {/* Lado Direito: Logo do Time */}
          <View style={styles.rightContent}>
            <FallbackImage
              sourceUrl={player.current_team_logo_url}
              textFallback={player.current_team_name || 'Time'}
              type="team"
              size={72}
              style={styles.teamLogo}
            />
          </View>
        </View>
      </TouchableOpacity>
    </Link>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E1E1E',
    borderRadius: 16,
    padding: spacing.xl,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  loadingCard: {
    height: 140,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  loadingText: {
    color: colors.textSecondary,
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.medium,
  },
  contentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    gap: spacing.md,
  },
  leftInfoBlock: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: spacing.md,
  },
  playerAvatar: {
    borderWidth: 2,
    borderColor: colors.secondary,
  },
  leftContent: {
    flex: 1,
  },
  rightContent: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 10,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 4,
  },
  name: {
    fontSize: 26,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    lineHeight: 32,
    marginBottom: spacing.xs,
  },
  statsLine: {
    fontSize: 11,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    lineHeight: 16,
  },
  teamLogo: {
    borderRadius: 8,
    borderWidth: 1.5,
    borderColor: '#333333',
  },
});

export default HighlightCard;
