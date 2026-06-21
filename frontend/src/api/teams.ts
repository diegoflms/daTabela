import { client } from './client';
import { ApiResponseList } from '../types/api';
import { Team } from '../types/models';

export const getTeams = (
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Team>> => {
  return client.get<ApiResponseList<Team>>(`/teams?limit=${limit}&offset=${offset}`);
};

export const getTeam = (id: number): Promise<Team> => {
  return client.get<Team>(`/teams/${id}`);
};

export const getTeamSeasons = (
  id: number,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<any>> => {
  return client.get<ApiResponseList<any>>(`/teams/${id}/seasons?limit=${limit}&offset=${offset}`);
};

export const getTeamGames = (
  id: number,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<any>> => {
  return client.get<ApiResponseList<any>>(`/teams/${id}/games?limit=${limit}&offset=${offset}`);
};
