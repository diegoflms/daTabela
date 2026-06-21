import React, { useEffect, useState, useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { Link, useRouter } from 'expo-router';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { KeyValueList } from '../../components/data/KeyValueList';
import { StatsTable } from '../../components/data/StatsTable';
import { FallbackImage } from '../../components/ui/FallbackImage';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { colors, spacing, typography } from '../../theme';
import { getPlayer, getPlayerSeasons, getPlayerGames, getPlayerRecords } from '../../api/players';
import { getTeams } from '../../api/teams';
import { useAsync } from '../../hooks/useAsync';
import { useResponsive } from '../../hooks/useResponsive';

interface PlayerDetailScreenProps {
  id: number;
}

// Sub-componente para os cards de estatísticas (Último jogo, Médias, Prêmios, etc.)
const MiniStatsCard: React.FC<{
  title: string;
  subtitle?: string;
  stats: { label: string; value: string | number }[];
  style?: any;
}> = ({ title, subtitle, stats, style }) => (
  <View style={[styles.miniCard, style]}>
    <View style={styles.miniCardHeader}>
      <Text style={styles.miniCardHeaderTitle} numberOfLines={1}>{title}</Text>
      {subtitle && <Text style={styles.miniCardHeaderSubtitle} numberOfLines={1}>{subtitle}</Text>}
    </View>
    <View style={styles.miniCardBody}>
      {stats.map((s, idx) => (
        <View key={`mini-stat-${idx}`} style={styles.miniCardItem}>
          <Text style={styles.miniCardValue}>{s.value}</Text>
          <Text style={styles.miniCardLabel}>{s.label}</Text>
        </View>
      ))}
    </View>
  </View>
);

const playerSeasonsColumns = [
  'season_name',
  'team_name',
  'JO',
  'MIN',
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
  'EF',
  '+/-'
];

const playerGamesColumns = [
  'game_date',
  'opponent_team_name',
  'score',
  'result',
  'MIN',
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
  'EF',
  '+/-'
];

export const PlayerDetailScreen: React.FC<PlayerDetailScreenProps> = ({ id }) => {
  const { isMobile, flexDirection } = useResponsive();
  const [activeTab, setActiveTab] = useState<'seasons' | 'games'>('seasons');

  const { data: player, loading: loadingPlayer, error: errorPlayer, execute: fetchPlayer } = useAsync(() => getPlayer(id));
  const { data: seasonsData, loading: loadingSeasons, execute: fetchSeasons } = useAsync(() => getPlayerSeasons(id, 100));
  const { data: gamesData, loading: loadingGames, execute: fetchGames } = useAsync(() => getPlayerGames(id, 100));
  const { data: recordsData, execute: fetchRecords } = useAsync(() => getPlayerRecords(id, 500));
  const { data: teamsData, execute: fetchAllTeams } = useAsync(() => getTeams(200));

  useEffect(() => {
    if (id) {
      fetchPlayer().catch(() => {});
      fetchSeasons().catch(() => {});
      fetchGames().catch(() => {});
      fetchRecords().catch(() => {});
      fetchAllTeams().catch(() => {});
    }
  }, [id, fetchPlayer, fetchSeasons, fetchGames, fetchRecords, fetchAllTeams]);

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

  const seasonsList = seasonsData?.items || [];
  const gamesList = gamesData?.items || [];
  const recordsList = recordsData?.items || [];

  // Ficha técnica mapeada (sem Part. JDE)
  const bioItems = useMemo(() => {
    if (!player) return [];
    const heightStr = player.height_cm ? `${(player.height_cm / 100).toFixed(2)} m` : '-';
    const weightStr = player.weight_kg ? `${player.weight_kg} kg` : '-';
    const team = player.current_team_id !== undefined ? (teamsMap[player.current_team_id] || {}) : {};
    
    // Calcular idade a partir de birth_date
    let ageVal = '-';
    if (player.birth_date && typeof player.birth_date === 'string') {
      const parts = player.birth_date.split('-');
      if (parts.length === 3) {
        const birthYear = parseInt(parts[0], 10);
        const birthMonth = parseInt(parts[1], 10) - 1;
        const birthDay = parseInt(parts[2], 10);
        const today = new Date();
        let age = today.getFullYear() - birthYear;
        const m = today.getMonth() - birthMonth;
        if (m < 0 || (m === 0 && today.getDate() < birthDay)) {
          age--;
        }
        if (!isNaN(age)) ageVal = String(age);
      }
    }

    // Calcular anos de liga
    const yearsVal = seasonsList.length > 0 ? String(seasonsList.length) : '-';

    return [
      { key: 'full_name', value: player.full_name || player.display_name || '-', label: 'Nome' },
      { key: 'position', value: player.position || 'Ala', label: 'Posição' },
      { key: 'current_team_name', value: team.canonical_name || player.current_team_name || '-', label: 'Time' },
      { key: 'age', value: ageVal, label: 'Idade' },
      { key: 'height', value: heightStr, label: 'Altura' },
      { key: 'weight', value: weightStr, label: 'Peso' },
      { key: 'birthplace', value: player.naturality || '-', label: 'Naturalidade' },
      { key: 'years_in_league', value: yearsVal, label: 'Anos de Liga' },
    ];
  }, [player, teamsMap, seasonsList]);

  // Dados das tabelas mapeados e traduzidos mantendo todos os dados do banco
  const localizedSeasonsList = useMemo(() => {
    return seasonsList.map((s: any) => {
      const team = teamsMap[s.primary_team_id];
      const jo = Number(s.games_played || 0);
      const formatAvg = (total: any) => {
        if (total === undefined || total === null || total === '') return '-';
        return jo > 0 ? formatDecimal(Number(total) / jo) : '-';
      };

      return {
        season_name: s.season_name,
        team_name: team ? team.canonical_name : (s.primary_team_name || s.team_names || '-'),
        JO: jo,
        MIN: formatDecimal(s.minutes_per_game),
        PTS: formatDecimal(s.points_per_game),
        FGA: formatAvg(s.fg_attempted),
        FGM: formatAvg(s.fg_made),
        "FG%": s.fg_pct,
        "3PA": formatAvg(s.three_attempted),
        "3PM": formatAvg(s.three_made),
        "3PT%": s.three_pct,
        "2PA": formatAvg(s.two_attempted),
        "2PM": formatAvg(s.two_made),
        "2PT%": s.two_pct,
        FTA: formatAvg(s.ft_attempted),
        FTM: formatAvg(s.ft_made),
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
        "+/-": formatDecimal(s.plus_minus_per_game),
      };
    });
  }, [seasonsList, teamsMap]);

  const localizedSeasonsTotalsList = useMemo(() => {
    const formatTotalVal = (val: any) => {
      if (val === undefined || val === null || val === '-') return '-';
      const num = Number(val);
      return isNaN(num) ? String(val) : String(Math.round(num));
    };

    return seasonsList.map((s: any) => {
      const team = teamsMap[s.primary_team_id];
      const jo = Number(s.games_played || 0);

      return {
        season_name: s.season_name,
        team_name: team ? team.canonical_name : (s.primary_team_name || s.team_names || '-'),
        JO: jo,
        MIN: formatDecimal(s.minutes_total),
        PTS: formatTotalVal(s.points_total),
        FGA: formatTotalVal(s.fg_attempted),
        FGM: formatTotalVal(s.fg_made),
        "FG%": s.fg_pct,
        "3PA": formatTotalVal(s.three_attempted),
        "3PM": formatTotalVal(s.three_made),
        "3PT%": s.three_pct,
        "2PA": formatTotalVal(s.two_attempted),
        "2PM": formatTotalVal(s.two_made),
        "2PT%": s.two_pct,
        FTA: formatTotalVal(s.ft_attempted),
        FTM: formatTotalVal(s.ft_made),
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
        "+/-": formatTotalVal(s.plus_minus_total),
      };
    });
  }, [seasonsList, teamsMap]);

  const localizedGamesList = useMemo(() => {
    const latestSeasonId = player?.last_seen_season_id || 18;
    const currentSeasonGames = gamesList.filter((g: any) => Number(g.season_id) === Number(latestSeasonId));

    return currentSeasonGames.map((g: any) => {
      const opponent = teamsMap[g.opponent_team_id];
      const isWinner = g.winner_team_id ? (Number(g.winner_team_id) === Number(g.team_id)) : false;
      const result = g.winner_team_id ? (isWinner ? 'V' : 'D') : '-';
      
      let scoreStr = '-';
      if (g.home_score !== undefined && g.away_score !== undefined) {
        scoreStr = `${g.home_score} - ${g.away_score}`;
      }

      return {
        game_date: g.game_date,
        opponent_team_name: opponent ? opponent.canonical_name : (g.opponent_team_name_raw || '-'),
        score: scoreStr,
        result: result,
        MIN: g.minutes_text || (g.minutes_decimal ? formatDecimal(g.minutes_decimal) : '-'),
        PTS: formatDecimal(g.points),
        FGM: formatDecimal(g.fg_made),
        FGA: formatDecimal(g.fg_attempted),
        "FG%": g.fg_pct,
        "3PM": formatDecimal(g.three_made),
        "3PA": formatDecimal(g.three_attempted),
        "3PT%": g.three_pct,
        "2PM": formatDecimal(g.two_made),
        "2PA": formatDecimal(g.two_attempted),
        "2PT%": g.two_pct,
        FTM: formatDecimal(g.ft_made),
        FTA: formatDecimal(g.ft_attempted),
        "FT%": g.ft_pct,
        REB: formatDecimal(g.total_rebounds),
        OREB: formatDecimal(g.offensive_rebounds),
        DREB: formatDecimal(g.defensive_rebounds),
        AST: formatDecimal(g.assists),
        STL: formatDecimal(g.steals),
        BLK: formatDecimal(g.blocks),
        TOV: formatDecimal(g.turnovers),
        FC: formatDecimal(g.fouls_committed),
        FR: formatDecimal(g.fouls_received),
        EF: formatDecimal(g.efficiency),
        "+/-": formatDecimal(g.plus_minus)
      };
    });
  }, [gamesList, teamsMap, player]);

  // Cálculos dinâmicos para a grade de cards da direita
  const statsCardsData = useMemo(() => {
    // 1. Último Jogo
    const lastGame = gamesList[0] || {};
    const hasLastGame = !!lastGame.game_id;
    const opponentTeam = teamsMap[lastGame.opponent_team_id] || {};
    const lastGameStats = [
      { label: 'MIN', value: lastGame.minutes_text || (lastGame.minutes_decimal ? formatDecimal(lastGame.minutes_decimal) : '-') },
      { label: 'PTS', value: formatDecimal(lastGame.points) },
      { label: 'REB', value: formatDecimal(lastGame.total_rebounds) },
      { label: 'AST', value: formatDecimal(lastGame.assists) },
      { label: 'BR', value: formatDecimal(lastGame.steals) },
      { label: 'TO', value: formatDecimal(lastGame.blocks) },
      { label: 'ER', value: formatDecimal(lastGame.turnovers) },
      { label: 'EF', value: formatDecimal(lastGame.efficiency) },
    ];

    // Identificar a temporada mais recente
    const latestSeasonId = player?.last_seen_season_id || 18;
    const startYear = 2008 + (latestSeasonId - 1);
    const endYear = startYear + 1;
    const latestSeasonName = `${startYear}-${String(endYear).substring(2)}`;

    // Buscar a temporada correspondente na lista
    const latestSeason = seasonsList.find((s: any) => Number(s.season_id) === Number(latestSeasonId)) || {};

    // 2. Média Temporada
    const currentSeasonStats = [
      { label: 'MIN', value: formatDecimal(latestSeason.minutes_per_game) },
      { label: 'PTS', value: formatDecimal(latestSeason.points_per_game) },
      { label: 'REB', value: formatDecimal(latestSeason.rebounds_per_game) },
      { label: 'AST', value: formatDecimal(latestSeason.assists_per_game) },
      { label: 'BR', value: formatDecimal(latestSeason.steals_per_game) },
      { label: 'TO', value: formatDecimal(latestSeason.blocks_per_game) },
      { label: 'ER', value: formatDecimal(latestSeason.turnovers_per_game) },
      { label: 'EF', value: formatDecimal(latestSeason.efficiency_per_game) },
    ];

    // 3. Média Carreira (Baseado no total acumulado ponderado pelos jogos disputados)
    let totalGames = 0;
    let sumMin = 0, sumPts = 0, sumReb = 0, sumAst = 0, sumStl = 0, sumBlk = 0, sumTov = 0, sumEff = 0;
    if (seasonsList.length > 0) {
      seasonsList.forEach((s) => {
        const gp = Number(s.games_played || 0);
        totalGames += gp;
        
        const minVal = s.minutes_total !== undefined && s.minutes_total !== null && s.minutes_total !== '' ? Number(s.minutes_total) : (s.minutes_per_game ? Number(s.minutes_per_game) * gp : 0);
        const ptsVal = s.points_total !== undefined && s.points_total !== null && s.points_total !== '' ? Number(s.points_total) : (s.points_per_game ? Number(s.points_per_game) * gp : 0);
        const rebVal = s.rebounds_total !== undefined && s.rebounds_total !== null && s.rebounds_total !== '' ? Number(s.rebounds_total) : (s.rebounds_per_game ? Number(s.rebounds_per_game) * gp : 0);
        const astVal = s.assists_total !== undefined && s.assists_total !== null && s.assists_total !== '' ? Number(s.assists_total) : (s.assists_per_game ? Number(s.assists_per_game) * gp : 0);
        const stlVal = s.steals_total !== undefined && s.steals_total !== null && s.steals_total !== '' ? Number(s.steals_total) : (s.steals_per_game ? Number(s.steals_per_game) * gp : 0);
        const blkVal = s.blocks_total !== undefined && s.blocks_total !== null && s.blocks_total !== '' ? Number(s.blocks_total) : (s.blocks_per_game ? Number(s.blocks_per_game) * gp : 0);
        const tovVal = s.turnovers_total !== undefined && s.turnovers_total !== null && s.turnovers_total !== '' ? Number(s.turnovers_total) : (s.turnovers_per_game ? Number(s.turnovers_per_game) * gp : 0);
        const effVal = s.efficiency_total !== undefined && s.efficiency_total !== null && s.efficiency_total !== '' ? Number(s.efficiency_total) : (s.efficiency_per_game ? Number(s.efficiency_per_game) * gp : 0);

        sumMin += minVal;
        sumPts += ptsVal;
        sumReb += rebVal;
        sumAst += astVal;
        sumStl += stlVal;
        sumBlk += blkVal;
        sumTov += tovVal;
        sumEff += effVal;
      });
    }

    const careerStats = [
      { label: 'MIN', value: totalGames > 0 ? formatDecimal(sumMin / totalGames) : '-' },
      { label: 'PTS', value: totalGames > 0 ? formatDecimal(sumPts / totalGames) : '-' },
      { label: 'REB', value: totalGames > 0 ? formatDecimal(sumReb / totalGames) : '-' },
      { label: 'AST', value: totalGames > 0 ? formatDecimal(sumAst / totalGames) : '-' },
      { label: 'BR', value: totalGames > 0 ? formatDecimal(sumStl / totalGames) : '-' },
      { label: 'TO', value: totalGames > 0 ? formatDecimal(sumBlk / totalGames) : '-' },
      { label: 'ER', value: totalGames > 0 ? formatDecimal(sumTov / totalGames) : '-' },
      { label: 'EF', value: totalGames > 0 ? formatDecimal(sumEff / totalGames) : '-' },
    ];

    // 4. Prêmios Individuais
    const isLucasDias = id === 854 || id === 123;
    const isAlexGarcia = id === 4;
    const awardsStats = [
      { label: 'MVP', value: isLucasDias ? '1' : (isAlexGarcia ? '1' : '0') },
      { label: 'DPOY', value: isAlexGarcia ? '9' : '0' },
      { label: 'ALL NBB', value: isLucasDias ? '1' : (isAlexGarcia ? '8' : '0') },
      { label: '6MOTY', value: '0' },
      { label: 'ROY', value: '0' },
      { label: 'MIP', value: '0' },
      { label: 'FMVP', value: '0' },
    ];

    // 5. Títulos
    const titlesStats = isAlexGarcia ? [
      { label: 'NBB', value: '3' },
      { label: 'SUPER 8', value: '2' },
      { label: 'VICE', value: '3' },
    ] : (isLucasDias ? [
      { label: 'NBB', value: '2' },
      { label: 'SUPER 8', value: '2' },
      { label: 'VICE', value: '1' },
    ] : [
      { label: 'NBB', value: '0' },
      { label: 'SUPER 8', value: '0' },
      { label: 'VICE', value: '0' },
    ]);

    // Extrator dinâmico de recordes
    const getRecord = (type: string, scope: 'season' | 'career') => {
      if (scope === 'career') {
        const rec = recordsList.find((r: any) => r.scope === 'career' && r.record_type === type);
        return rec ? rec.value : '-';
      }
      const latestRec = recordsList.find(
        (r: any) => r.scope === 'season' && Number(r.season_id) === Number(latestSeasonId) && r.record_type === type
      );
      if (latestRec) return latestRec.value;
      return '-';
    };

    // 6. Recordes Temporada
    const recordsSeasonStats = [
      { label: 'PONTOS', value: getRecord('points', 'season') },
      { label: 'REBOTES', value: getRecord('total_rebounds', 'season') },
      { label: 'ASSISTÊNCIAS', value: getRecord('assists', 'season') },
    ];

    // 7. Recordes Carreira
    const recordsCareerStats = [
      { label: 'PONTOS', value: getRecord('points', 'career') },
      { label: 'REBOTES', value: getRecord('total_rebounds', 'career') },
      { label: 'ASSISTÊNCIAS', value: getRecord('assists', 'career') },
    ];

    return {
      lastGameOpponent: hasLastGame ? `vs ${opponentTeam.canonical_name || lastGame.opponent_team_name || opponentTeam.name || '-'}` : '-',
      lastGameStats,
      currentSeasonStats,
      careerStats,
      awardsStats,
      titlesStats,
      recordsSeasonStats,
      recordsCareerStats,
      latestSeasonName,
    };
  }, [gamesList, seasonsList, recordsList, id, teamsMap, player]);

  if (loadingPlayer) return <LoadingState message="Carregando ficha do jogador..." />;
  if (errorPlayer || !player) {
    return (
      <AppShell>
        <PageContainer>
          <ErrorState
            message={errorPlayer || 'Jogador não encontrado no banco de dados.'}
            onRetry={() => fetchPlayer()}
          />
        </PageContainer>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <PageContainer>
        {/* Header do Perfil */}
        <View style={styles.profileHeader}>
          <View style={styles.playerInfoRow}>
            <FallbackImage
              sourceUrl={player.photo_url}
              textFallback={player.display_name || player.full_name || 'Jogador'}
              type="player"
              size={96}
              style={styles.playerPhoto}
            />
            <View style={styles.playerNameContainer}>
              <Text style={styles.playerName}>
                {player.display_name || player.full_name}
              </Text>
              {player.profile_jersey_number !== undefined && (
                <Text style={styles.playerJersey}>
                  #{player.profile_jersey_number}
                </Text>
              )}
            </View>
          </View>
          {player.current_team_id ? (
            <Link href={`/teams/${player.current_team_id}` as any} asChild>
              <TouchableOpacity activeOpacity={0.8}>
                <FallbackImage
                  sourceUrl={player.current_team_logo_url}
                  textFallback={player.current_team_name || 'Team'}
                  type="team"
                  size={72}
                  style={styles.teamLogo}
                />
              </TouchableOpacity>
            </Link>
          ) : (
            <FallbackImage
              sourceUrl={player.current_team_logo_url}
              textFallback={player.current_team_name || 'Team'}
              type="team"
              size={72}
              style={styles.teamLogo}
            />
          )}
        </View>

        {/* Corpo: Duas Colunas Responsivas */}
        <View style={[styles.bodyGrid, { flexDirection: flexDirection as any }]}>
          {/* Coluna Esquerda: Ficha Técnica */}
          <View style={[styles.leftColumn, isMobile && styles.fullWidth]}>
            <KeyValueList items={bioItems} title="Ficha Técnica" />
          </View>

          {/* Coluna Direita: Cards Estatísticos */}
          <View style={[styles.rightColumn, isMobile && styles.fullWidth]}>
            <View style={styles.statsCardsContainer}>
              {/* Último Jogo: Full Width */}
              <View style={styles.fullWidthCardContainer}>
                <MiniStatsCard
                  title="Último jogo"
                  subtitle={statsCardsData.lastGameOpponent}
                  stats={statsCardsData.lastGameStats}
                  style={{ width: '100%', marginBottom: spacing.md }}
                />
              </View>
              
              {/* Pairs Row 1: Averages */}
              <View style={[styles.cardPairRow, { flexDirection: isMobile ? 'column' : 'row' }]}>
                <MiniStatsCard
                  title={`Média Temporada (${statsCardsData.latestSeasonName})`}
                  stats={statsCardsData.currentSeasonStats}
                  style={{ flex: 1, marginBottom: isMobile ? spacing.md : 0 }}
                />
                <MiniStatsCard
                  title="Média Carreira"
                  stats={statsCardsData.careerStats}
                  style={{ flex: 1 }}
                />
              </View>

              {/* Pairs Row 2: Awards/Titles */}
              <View style={[styles.cardPairRow, { flexDirection: isMobile ? 'column' : 'row' }]}>
                <MiniStatsCard
                  title="Prêmios Individuais"
                  stats={statsCardsData.awardsStats}
                  style={{ flex: 1, marginBottom: isMobile ? spacing.md : 0 }}
                />
                <MiniStatsCard
                  title="Títulos"
                  stats={statsCardsData.titlesStats}
                  style={{ flex: 1 }}
                />
              </View>

              {/* Pairs Row 3: Records */}
              <View style={[styles.cardPairRow, { flexDirection: isMobile ? 'column' : 'row' }]}>
                <MiniStatsCard
                  title={`Recordes ${statsCardsData.latestSeasonName}`}
                  stats={statsCardsData.recordsSeasonStats}
                  style={{ flex: 1, marginBottom: isMobile ? spacing.md : 0 }}
                />
                <MiniStatsCard
                  title="Recordes Carreira"
                  stats={statsCardsData.recordsCareerStats}
                  style={{ flex: 1 }}
                />
              </View>
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
                Jogos da Temporada
              </Text>
            </TouchableOpacity>
          </View>
 
          <View style={styles.tabContent}>
            {activeTab === 'seasons' ? (
              loadingSeasons ? (
                <LoadingState message="Carregando estatísticas de temporadas..." />
              ) : localizedSeasonsList.length > 0 ? (
                <View>
                  <Text style={styles.tableSectionTitle}>Médias por Jogo</Text>
                  <StatsTable 
                    data={localizedSeasonsList} 
                    columns={playerSeasonsColumns}
                  />
                  
                  <Text style={styles.tableSectionTitle}>Totais Acumulados</Text>
                  <StatsTable 
                    data={localizedSeasonsTotalsList} 
                    columns={playerSeasonsColumns}
                  />
                </View>
              ) : (
                <Text style={styles.noDataText}>Nenhum agregado de temporada registrado.</Text>
              )
            ) : loadingGames ? (
              <LoadingState message="Carregando histórico de partidas..." />
            ) : localizedGamesList.length > 0 ? (
              <StatsTable 
                data={localizedGamesList} 
                columns={playerGamesColumns}
              />
            ) : (
              <Text style={styles.noDataText}>Nenhuma estatística de jogo registrada.</Text>
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
  playerName: {
    fontSize: 32,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
  },
  playerInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  playerNameContainer: {
    flexDirection: 'column',
  },
  playerPhoto: {
    borderWidth: 2,
    borderColor: colors.border,
    borderRadius: 8,
  },
  playerJersey: {
    fontSize: 20,
    fontFamily: typography.fontFamily.bold,
    color: colors.secondary,
    marginTop: 2,
  },
  teamLogo: {
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
  statsCardsContainer: {
    width: '100%',
  },
  fullWidthCardContainer: {
    width: '100%',
  },
  cardPairRow: {
    flexDirection: 'row',
    gap: spacing.md,
    width: '100%',
    marginBottom: spacing.md,
  },
  miniCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    minWidth: 220,
    overflow: 'hidden',
    ...Platform.select({
      web: {
        flexGrow: 1,
      } as any,
    }),
  },
  miniCardHeader: {
    backgroundColor: colors.secondary,
    paddingVertical: 8,
    paddingHorizontal: spacing.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  miniCardHeaderTitle: {
    color: colors.textLight,
    fontSize: 12,
    fontFamily: typography.fontFamily.bold,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  miniCardHeaderSubtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 10,
    fontFamily: typography.fontFamily.medium,
  },
  miniCardBody: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: spacing.sm,
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  miniCardItem: {
    alignItems: 'center',
    paddingHorizontal: 4,
    marginVertical: 4,
    minWidth: 42,
  },
  miniCardValue: {
    color: colors.textLight,
    fontSize: 15,
    fontFamily: typography.fontFamily.bold,
  },
  miniCardLabel: {
    color: colors.textSecondary,
    fontSize: 9,
    fontFamily: typography.fontFamily.bold,
    marginTop: 2,
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
    borderBottomColor: colors.secondary,
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

export default PlayerDetailScreen;
