import React, { useEffect, useState, useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { KeyValueList } from '../../components/data/KeyValueList';
import { StatsTable } from '../../components/data/StatsTable';
import { FallbackImage } from '../../components/ui/FallbackImage';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { colors, spacing, typography } from '../../theme';
import { getTeam, getTeamSeasons, getTeamGames, getTeams } from '../../api/teams';
import { useAsync } from '../../hooks/useAsync';
import { useResponsive } from '../../hooks/useResponsive';
import { LeaderboardCard } from '../home/LeaderboardCard';

interface TeamDetailScreenProps {
  id: number;
}

// Sub-componente para cards horizontais de partidas (Último jogo)
const GameScheduleCard: React.FC<{
  title: string;
  subtitle: string;
  teamA: string;
  teamB: string;
  scoreOrTime: string;
  badgeA: string;
  badgeB: string;
  style?: any;
}> = ({ title, subtitle, teamA, teamB, scoreOrTime, badgeA, badgeB, style }) => (
  <View style={[styles.scheduleCard, style]}>
    <View style={styles.scheduleHeader}>
      <Text style={styles.scheduleTitle}>{title}</Text>
      <Text style={styles.scheduleSubtitle}>{subtitle}</Text>
    </View>
    <View style={styles.scheduleBody}>
      <View style={styles.scheduleTeam}>
        <Text style={styles.scheduleTeamName}>{teamA}</Text>
      </View>
      <Text style={styles.scheduleScore}>{scoreOrTime}</Text>
      <View style={styles.scheduleTeam}>
        <Text style={styles.scheduleTeamName}>{teamB}</Text>
      </View>
    </View>
  </View>
);

const teamSeasonsColumns = [
  'season_name',
  'JO',
  'VIT',
  'DER',
  'AP(%)',
  'PTS',
  'FGM',
  'FGA',
  'FG%',
  '3PM',
  '3PA',
  '3PT%',
  '2PM',
  '2PA',
  '2PT%',
  'FTM',
  'FTA',
  'FT%',
  'REB',
  'OREB',
  'DREB',
  'AST',
  'STL',
  'BLK',
  'TOV',
  'FC',
  'FR',
  'EF'
];

export const TeamDetailScreen: React.FC<TeamDetailScreenProps> = ({ id }) => {
  const { isMobile, flexDirection } = useResponsive();
  const [activeTab, setActiveTab] = useState<'seasons' | 'games'>('seasons');

  const { data: team, loading: loadingTeam, error: errorTeam, execute: fetchTeam } = useAsync(() => getTeam(id));
  const { data: seasonsData, loading: loadingSeasons, execute: fetchSeasons } = useAsync(() => getTeamSeasons(id));
  const { data: gamesData, loading: loadingGames, execute: fetchGames } = useAsync(() => getTeamGames(id));
  const { data: teamsData, execute: fetchAllTeams } = useAsync(() => getTeams(200));

  useEffect(() => {
    if (id) {
      fetchTeam().catch(() => {});
      fetchSeasons().catch(() => {});
      fetchGames().catch(() => {});
      fetchAllTeams().catch(() => {});
    }
  }, [id, fetchTeam, fetchSeasons, fetchGames, fetchAllTeams]);

  // Map de equipes para traduzir IDs em nomes canônicos e logos
  const teamsMap = useMemo(() => {
    const map: Record<number, any> = {};
    if (teamsData?.items) {
      teamsData.items.forEach((t: any) => {
        map[t.id] = t;
      });
    }
    return map;
  }, [teamsData]);

  const formatDecimal = (val: any) => {
    if (val === undefined || val === null || val === '-') return '-';
    const num = Number(val);
    return isNaN(num) ? String(val) : num.toFixed(1);
  };

  const bioItems = useMemo(() => {
    if (!team) return [];
    
    const firstSeasonId = team.first_seen_season_id || 1;
    const lastSeasonId = team.last_seen_season_id || 18;
    const totalSeasons = lastSeasonId - firstSeasonId + 1;

    const getSeasonName = (id: number) => {
      const startYear = 2008 + (id - 1);
      const endYear = startYear + 1;
      const endYearStr = String(endYear).substring(2);
      return `${startYear}-${endYearStr}`;
    };

    return [
      { key: 'canonical_name', value: team.canonical_name || team.name, label: 'Nome' },
      { key: 'city', value: team.city || '-', label: 'Cidade' },
      { key: 'state', value: team.state || '-', label: 'Estado' },
      { key: 'abbreviation', value: team.abbreviation || '-', label: 'Abreviação' },
      { key: 'arena_name', value: team.arena_name || 'Ginásio do Clube', label: 'Ginásio' },
      { key: 'first_season', value: getSeasonName(firstSeasonId), label: 'Primeira Temporada' },
      { key: 'last_season', value: getSeasonName(lastSeasonId), label: 'Última Temporada' },
      { key: 'total_seasons', value: `${totalSeasons} temporada(s)`, label: 'Total de Temporadas' },
      { key: 'titles_nbb', value: team.titles_nbb || 0, label: 'Títulos NBB' },
      { key: 'titles_super_8', value: team.titles_super_8 || 0, label: 'Títulos Copa Super 8' },
    ];
  }, [team]);

  const seasonsList = seasonsData?.items || [];
  const gamesList = gamesData?.items || [];

  // Dados das partidas (Último jogo)
  const scheduleData = useMemo(() => {
    const lastGame = gamesList[0];
    const hasLastGame = !!lastGame;

    if (!hasLastGame) {
      return {
        lastGameTitle: 'Último jogo',
        lastGameSub: '-',
        lastGameTeamA: team?.abbreviation || '-',
        lastGameTeamB: '-',
        lastGameScore: '-',
      };
    }

    const homeTeam = teamsMap[lastGame.home_team_id];
    const awayTeam = teamsMap[lastGame.away_team_id];

    const homeAbbr = homeTeam?.abbreviation || lastGame.home_team_abbr_raw || '-';
    const awayAbbr = awayTeam?.abbreviation || lastGame.away_team_abbr_raw || '-';
    const scoreStr = `${lastGame.home_score} - ${lastGame.away_score}`;
    
    let dateStr = '-';
    if (lastGame.game_date) {
      const parts = lastGame.game_date.split('-');
      if (parts.length === 3) {
        dateStr = `${parts[2]}/${parts[1]}/${parts[0]}`;
      } else {
        dateStr = lastGame.game_date;
      }
    }

    return {
      lastGameTitle: 'Último jogo',
      lastGameSub: `${dateStr} (${lastGame.round || ''})`,
      lastGameTeamA: homeAbbr,
      lastGameTeamB: awayAbbr,
      lastGameScore: scoreStr,
    };
  }, [gamesList, team, teamsMap]);

  const localizedSeasonsList = useMemo(() => {
    return seasonsList.map((s: any) => {
      const jo = Number(s.wins || 0) + Number(s.losses || 0); // J da temporada regular (V + D)
      const formatAvg = (total: any) => {
        if (total === undefined || total === null || total === '') return '-';
        return jo > 0 ? formatDecimal(Number(total) / jo) : '-';
      };

      return {
        season_name: s.season_name,
        JO: jo,
        VIT: s.wins,
        DER: s.losses,
        "AP(%)": s.ap_pct,
        PTS: formatDecimal(s.points_per_game),
        FGM: formatAvg(s.fg_made),
        FGA: formatAvg(s.fg_attempted),
        "FG%": s.fg_pct,
        "3PM": formatAvg(s.three_made),
        "3PA": formatAvg(s.three_attempted),
        "3PT%": s.three_pct,
        "2PM": formatAvg(s.two_made),
        "2PA": formatAvg(s.two_attempted),
        "2PT%": s.two_pct,
        FTM: formatAvg(s.ft_made),
        FTA: formatAvg(s.ft_attempted),
        "FT%": s.ft_pct,
        REB: formatDecimal(s.rebounds_per_game),
        OREB: formatAvg(s.offensive_rebounds_total),
        DREB: formatAvg(s.defensive_rebounds_total),
        AST: formatDecimal(s.assists_per_game),
        STL: formatDecimal(s.steals_per_game),
        BLK: formatDecimal(s.blocks_per_game),
        TOV: formatDecimal(s.turnovers_per_game),
        FC: formatAvg(s.fouls_committed_total),
        FR: formatAvg(s.fouls_received_total),
        EF: formatDecimal(s.efficiency_per_game),
      };
    });
  }, [seasonsList]);

  const localizedSeasonsTotalsList = useMemo(() => {
    const formatTotalVal = (val: any) => {
      if (val === undefined || val === null || val === '-') return '-';
      const num = Number(val);
      return isNaN(num) ? String(val) : String(Math.round(num));
    };

    return seasonsList.map((s: any) => {
      const jo = Number(s.wins || 0) + Number(s.losses || 0);

      return {
        season_name: s.season_name,
        JO: jo,
        VIT: s.wins,
        DER: s.losses,
        "AP(%)": s.ap_pct,
        PTS: formatTotalVal(s.points_total),
        FGM: formatTotalVal(s.fg_made),
        FGA: formatTotalVal(s.fg_attempted),
        "FG%": s.fg_pct,
        "3PM": formatTotalVal(s.three_made),
        "3PA": formatTotalVal(s.three_attempted),
        "3PT%": s.three_pct,
        "2PM": formatTotalVal(s.two_made),
        "2PA": formatTotalVal(s.two_attempted),
        "2PT%": s.two_pct,
        FTM: formatTotalVal(s.ft_made),
        FTA: formatTotalVal(s.ft_attempted),
        "FT%": s.ft_pct,
        REB: formatTotalVal(s.rebounds_total),
        OREB: formatTotalVal(s.offensive_rebounds_total),
        DREB: formatTotalVal(s.defensive_rebounds_total),
        AST: formatTotalVal(s.assists_total),
        STL: formatTotalVal(s.steals_total),
        BLK: formatTotalVal(s.blocks_total),
        TOV: formatTotalVal(s.turnovers_total),
        FC: formatTotalVal(s.fouls_committed_total),
        FR: formatTotalVal(s.fouls_received_total),
        EF: formatTotalVal(s.efficiency_total),
      };
    });
  }, [seasonsList]);

  const localizedGamesList = useMemo(() => {
    return gamesList.map((g: any) => {
      const homeTeam = teamsMap[g.home_team_id];
      const awayTeam = teamsMap[g.away_team_id];
      
      const homeName = homeTeam ? homeTeam.canonical_name : g.home_team_name_raw;
      const awayName = awayTeam ? awayTeam.canonical_name : g.away_team_name_raw;

      return {
        game_date: g.game_date,
        home_team_name: homeName,
        score: `${g.home_score} - ${g.away_score}`,
        away_team_name: awayName,
        phase: g.phase,
        arena: g.arena,
      };
    });
  }, [gamesList, teamsMap]);

  if (loadingTeam) return <LoadingState message="Carregando dados da equipe..." />;
  if (errorTeam || !team) {
    return (
      <AppShell>
        <PageContainer>
          <ErrorState
            message={errorTeam || 'Equipe não encontrada no banco SQLite.'}
            onRetry={() => fetchTeam()}
          />
        </PageContainer>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <PageContainer>
        {/* Header do Time */}
        <View style={styles.profileHeader}>
          <Text style={styles.teamName}>{team.canonical_name || team.name}</Text>
          <FallbackImage
            sourceUrl={team.logo_url}
            textFallback={team.canonical_name || team.name}
            type="team"
            size={72}
            style={styles.logo}
          />
        </View>

        {/* Corpo: Duas Colunas Responsivas */}
        <View style={[styles.bodyGrid, { flexDirection: flexDirection as any }]}>
          {/* Esquerda: Ficha Técnica */}
          <View style={[styles.leftColumn, isMobile && styles.fullWidth]}>
            <KeyValueList items={bioItems} title="Ficha Técnica" />
          </View>

          {/* Direita: Abas e Históricos */}
          <View style={[styles.rightColumn, isMobile && styles.fullWidth]}>
            {/* Card de Partida Recente */}
            <View style={styles.scheduleRow}>
              <GameScheduleCard
                title={scheduleData.lastGameTitle}
                subtitle={scheduleData.lastGameSub}
                teamA={scheduleData.lastGameTeamA}
                teamB={scheduleData.lastGameTeamB}
                scoreOrTime={scheduleData.lastGameScore}
                badgeA={team.canonical_name || team.name}
                badgeB="Adversário"
                style={{ width: '100%', marginBottom: spacing.md }}
              />
            </View>

            {/* Líderes Estatísticos */}
            <Text style={styles.sectionTitle}>Líderes da Equipe (Média da Temporada)</Text>
            <View style={styles.leadersGrid}>
              <LeaderboardCard metric="points_per_game" title="Pontos por Jogo" teamId={id} seasonId={18} />
              <LeaderboardCard metric="assists_per_game" title="Assistências" teamId={id} seasonId={18} />
              <LeaderboardCard metric="rebounds_per_game" title="Rebotes" teamId={id} seasonId={18} />
            </View>
          </View>
        </View>

        {/* Abas e Tabelas Inferiores */}
        <View style={styles.tabsContainer}>
          <View style={styles.tabRow}>
            <TouchableOpacity
              style={[styles.tab, activeTab === 'seasons' && styles.activeTab]}
              onPress={() => setActiveTab('seasons')}
              activeOpacity={0.7}
            >
              <Text style={[styles.tabText, activeTab === 'seasons' && styles.activeTabText]}>
                Temporadas
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.tab, activeTab === 'games' && styles.activeTab]}
              onPress={() => setActiveTab('games')}
              activeOpacity={0.7}
            >
              <Text style={[styles.tabText, activeTab === 'games' && styles.activeTabText]}>
                Partidas da Temporada
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.tabContent}>
            {activeTab === 'seasons' ? (
              loadingSeasons ? (
                <LoadingState message="Carregando temporadas..." />
              ) : localizedSeasonsList.length > 0 ? (
                <View>
                  <Text style={styles.tableSectionTitle}>Médias por Jogo</Text>
                  <StatsTable 
                    data={localizedSeasonsList} 
                    columns={teamSeasonsColumns}
                  />
                  
                  <Text style={styles.tableSectionTitle}>Totais Acumulados</Text>
                  <StatsTable 
                    data={localizedSeasonsTotalsList} 
                    columns={teamSeasonsColumns}
                  />
                </View>
              ) : (
                <Text style={styles.noDataText}>Nenhum registro de temporada para esta equipe.</Text>
              )
            ) : loadingGames ? (
              <LoadingState message="Carregando histórico de partidas..." />
            ) : localizedGamesList.length > 0 ? (
              <StatsTable 
                data={localizedGamesList} 
                columns={['game_date', 'home_team_name', 'score', 'away_team_name', 'phase', 'arena']}
              />
            ) : (
              <Text style={styles.noDataText}>Nenhuma partida registrada.</Text>
            )}
          </View>
        </View>
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    width: '100%',
  },
  teamName: {
    fontSize: 36,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
  },
  logo: {
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  bodyGrid: {
    width: '100%',
    gap: spacing.lg,
  },
  leftColumn: {
    flex: 3,
  },
  rightColumn: {
    flex: 7,
  },
  fullWidth: {
    width: '100%',
  },
  scheduleRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: spacing.md,
  },
  // Cards de agenda/partida estilizados
  scheduleCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    width: '48%',
    minWidth: 235,
    marginBottom: spacing.sm,
    overflow: 'hidden',
    ...Platform.select({
      web: {
        flexGrow: 1,
      } as any,
    }),
  },
  scheduleHeader: {
    backgroundColor: colors.secondary, // Laranja
    paddingVertical: 8,
    paddingHorizontal: spacing.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  scheduleTitle: {
    color: colors.textLight,
    fontSize: 12,
    fontFamily: typography.fontFamily.bold,
    textTransform: 'uppercase',
  },
  scheduleSubtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 10,
    fontFamily: typography.fontFamily.medium,
  },
  scheduleBody: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    padding: spacing.md,
    backgroundColor: '#1E1E1E',
  },
  scheduleTeam: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  scheduleTeamName: {
    color: colors.textLight,
    fontSize: 14,
    fontFamily: typography.fontFamily.bold,
  },
  scheduleScore: {
    color: colors.accent,
    fontSize: 18,
    fontFamily: typography.fontFamily.bold,
    textAlign: 'center',
    flex: 1,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  leadersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    width: '100%',
  },
  tabsContainer: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    marginTop: spacing.xl,
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
    borderBottomColor: colors.secondary, // Linha inferior laranja
  },
  tabText: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
    color: colors.textSecondary,
  },
  activeTabText: {
    color: colors.secondary,
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
  tableSectionTitle: {
    fontSize: 18,
    fontFamily: typography.fontFamily.bold,
    color: colors.secondary, // Laranja do tema
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
});
export default TeamDetailScreen;
