export type AskStatus = 'ok' | 'needs_clarification' | 'not_found' | 'unsupported';

export interface AskInterpretedAs {
  intent: string;
  player_query?: string;
  last_n_games?: number;
  player?: {
    id: number;
    name: string;
    matched_via?: string;
    matched_value?: string;
  };
  target?: string;
  metric?: string;
  metric_column?: string;
  top_n?: number;
  source_table?: string;
  aggregation?: string;
  [key: string]: any;
}

export interface AskResponse {
  status: AskStatus;
  question: string;
  title?: string;
  interpreted_as?: AskInterpretedAs;
  source_tables?: string[];
  columns: string[];
  rows: Record<string, any>[];
  total?: number;
  message?: string;
  candidates?: any[];
  supported_examples?: string[];
  note?: string;
}

export interface AskRequest {
  question: string;
}
