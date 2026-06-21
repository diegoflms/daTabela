export interface ApiResponseList<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface GlobalSearchResponse {
  players: any[];
  teams: any[];
  games: any[];
  query: string;
}
