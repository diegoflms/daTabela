import { client } from './client';
import { ApiResponseList } from '../types/api';
import { Player } from '../types/models';

export const getPlayers = (
  q?: string,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Player>> => {
  const queryParam = q ? `q=${encodeURIComponent(q)}&` : '';
  return client.get<ApiResponseList<Player>>(`/players?${queryParam}limit=${limit}&offset=${offset}`);
};

export const getPlayer = (id: number): Promise<Player> => {
  return client.get<Player>(`/players/${id}`);
};

export const getPlayerSeasons = (
  id: number,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<any>> => {
  return client.get<ApiResponseList<any>>(`/players/${id}/seasons?limit=${limit}&offset=${offset}`);
};

export const getPlayerGames = (
  id: number,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<any>> => {
  return client.get<ApiResponseList<any>>(`/players/${id}/games?limit=${limit}&offset=${offset}`);
};

export const getPlayerRecords = (
  id: number,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<any>> => {
  return client.get<ApiResponseList<any>>(`/players/${id}/records?limit=${limit}&offset=${offset}`);
};
