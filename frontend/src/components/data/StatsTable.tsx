import React from 'react';
import { ViewStyle } from 'react-native';
import { DynamicTable } from './DynamicTable';

interface StatsTableProps {
  data: Record<string, any>[];
  columns?: string[];
  style?: ViewStyle;
}

export const StatsTable: React.FC<StatsTableProps> = ({ data, columns, style }) => {
  // Se nenhuma coluna for fornecida, extrai as chaves do primeiro objeto dos dados
  const displayColumns = columns || (data && data.length > 0 ? Object.keys(data[0]) : []);
  
  // Remove colunas administrativas do banco como 'id', 'player_id', 'team_id', 'season_id'
  const filteredColumns = displayColumns.filter(
    (col) => !['id', 'player_id', 'team_id', 'season_id', 'created_at', 'updated_at'].includes(col)
  );

  return <DynamicTable columns={filteredColumns} rows={data} style={style} />;
};

export default StatsTable;
