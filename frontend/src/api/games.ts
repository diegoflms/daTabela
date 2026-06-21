import { client } from './client';
import { ApiResponseList } from '../types/api';
import { Game } from '../types/models';

export const getGames = (
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Game>> => {
  return client.get<ApiResponseList<Game>>(`/games?limit=${limit}&offset=${offset}`);
};

export const getGame = (id: number): Promise<Game> => {
  return client.get<Game>(`/games/${id}`);
};

export const getGamePlayerStats = (id: number): Promise<any> => {
  return client.get<any>(`/games/${id}/player-stats`);
};

export const getGameTeamStats = (id: number): Promise<any> => {
  return client.get<any>(`/games/${id}/team-stats`);
};
