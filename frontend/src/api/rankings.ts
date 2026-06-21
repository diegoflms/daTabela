import { client } from './client';

export const getPlayerRankingMetrics = (): Promise<{ metrics: string[] }> => {
  return client.get<{ metrics: string[] }>('/rankings/players/metrics');
};

export const getPlayerRanking = (metric: string, seasonId?: number, teamId?: number): Promise<any> => {
  const params: string[] = [];
  if (seasonId) params.push(`season_id=${seasonId}`);
  if (teamId) params.push(`team_id=${teamId}`);
  const query = params.length > 0 ? `?${params.join('&')}` : '';
  return client.get<any>(`/rankings/players/${metric}${query}`);
};

export const getTeamRankingMetrics = (): Promise<{ metrics: string[] }> => {
  return client.get<{ metrics: string[] }>('/rankings/teams/metrics');
};

export const getTeamRanking = (metric: string, seasonId?: number): Promise<any> => {
  const query = seasonId ? `?season_id=${seasonId}` : '';
  return client.get<any>(`/rankings/teams/${metric}${query}`);
};
