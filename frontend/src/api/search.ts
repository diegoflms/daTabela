import { client } from './client';
import { ApiResponseList, GlobalSearchResponse } from '../types/api';
import { Player, Team, Game } from '../types/models';

export const globalSearch = (q: string, limit: number = 10): Promise<GlobalSearchResponse> => {
  return client.get<GlobalSearchResponse>(`/search?q=${encodeURIComponent(q)}&limit=${limit}`);
};

export const searchPlayers = (
  q: string,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Player>> => {
  return client.get<ApiResponseList<Player>>(
    `/search/players?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`
  );
};

export const searchTeams = (
  q: string,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Team>> => {
  return client.get<ApiResponseList<Team>>(
    `/search/teams?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`
  );
};

export const searchGames = (
  q: string,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Game>> => {
  return client.get<ApiResponseList<Game>>(
    `/search/games?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`
  );
};
