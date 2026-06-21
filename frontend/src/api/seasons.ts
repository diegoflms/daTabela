import { client } from './client';
import { ApiResponseList } from '../types/api';
import { Season, Standing } from '../types/models';

export const getSeasons = (
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Season>> => {
  return client.get<ApiResponseList<Season>>(`/seasons?limit=${limit}&offset=${offset}`);
};

export const getStandings = (
  seasonId?: number,
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponseList<Standing>> => {
  const queryParam = seasonId ? `season_id=${seasonId}&` : '';
  return client.get<ApiResponseList<Standing>>(`/standings?${queryParam}limit=${limit}&offset=${offset}`);
};
