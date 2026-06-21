import React from 'react';
import { View, Text, StyleSheet, ScrollView, ViewStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme';
import { formatColumnLabel } from '../../utils/labels';
import { formatCellValue } from '../../utils/formatters';

interface DynamicTableProps {
  columns: string[];
  rows: Record<string, any>[];
  style?: ViewStyle;
}

export const DynamicTable: React.FC<DynamicTableProps> = ({ columns, rows, style }) => {
  if (!columns || columns.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>Tabela sem colunas a serem exibidas.</Text>
      </View>
    );
  }

  // Identifica a largura aproximada de cada coluna.
  // Colunas de strings longas ganham mais espaço, colunas de estatísticas encurtam.
  const getColWidth = (col: string) => {
    const colLower = col.toLowerCase();
    if (
      colLower.includes('name') || 
      colLower.includes('alias') || 
      colLower.includes('title') || 
      colLower.includes('arena') || 
      colLower.includes('venue') ||
      colLower.includes('interpreted')
    ) {
      return 180;
    }
    if (colLower.includes('date') || colLower.includes('url')) {
      return 140;
    }
    // Estatísticas puras (PTS, AST, REB, etc.)
    return 90;
  };

  return (
    <ScrollView 
      horizontal={true} 
      showsHorizontalScrollIndicator={true} 
      style={[styles.outerScroll, style]}
    >
      <View style={styles.tableContainer}>
        {/* Header */}
        <View style={styles.tableRowHeader}>
          {columns.map((col, idx) => {
            const width = getColWidth(col);
            return (
              <View 
                key={`header-${col}-${idx}`} 
                style={[styles.tableCellHeader, { width }]}
              >
                <Text style={styles.tableCellHeaderText}>
                  {formatColumnLabel(col)}
                </Text>
              </View>
            );
          })}
        </View>

        {/* Rows */}
        {rows && rows.length > 0 ? (
          rows.map((row, rowIdx) => (
            <View
              key={`row-${rowIdx}`}
              style={[
                styles.tableRow,
                rowIdx % 2 === 1 && styles.tableRowAlternate,
                rowIdx === rows.length - 1 && styles.lastRow,
              ]}
            >
              {columns.map((col, colIdx) => {
                const width = getColWidth(col);
                return (
                  <View 
                    key={`cell-${rowIdx}-${col}-${colIdx}`} 
                    style={[styles.tableCell, { width }]}
                  >
                    <Text style={styles.tableCellText}>
                      {formatCellValue(row[col], col)}
                    </Text>
                  </View>
                );
              })}
            </View>
          ))
        ) : (
          <View style={styles.noRowsContainer}>
            <Text style={styles.noRowsText}>Nenhum registro encontrado para esta tabela.</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  outerScroll: {
    width: '100%',
    marginVertical: spacing.md,
    borderRadius: 8,
  },
  tableContainer: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: colors.surface,
    minWidth: '100%',
  },
  tableRowHeader: {
    flexDirection: 'row',
    backgroundColor: colors.secondary,
    borderBottomWidth: 1,
    borderBottomColor: colors.secondaryDark,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  tableCellHeader: {
    justifyContent: 'center',
    paddingHorizontal: spacing.xs,
  },
  tableCellHeaderText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textAlign: 'left',
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    alignItems: 'center',
    backgroundColor: colors.surface,
  },
  tableRowAlternate: {
    backgroundColor: '#252525',
  },
  lastRow: {
    borderBottomWidth: 0,
  },
  tableCell: {
    justifyContent: 'center',
    paddingHorizontal: spacing.xs,
  },
  tableCellText: {
    fontSize: typography.fontSize.sm,
    color: colors.text,
    fontFamily: typography.fontFamily.regular,
  },
  emptyContainer: {
    padding: spacing.xl,
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: typography.fontSize.md,
  },
  noRowsContainer: {
    padding: spacing.xl,
    alignItems: 'center',
    width: '100%',
  },
  noRowsText: {
    color: colors.textMuted,
    fontSize: typography.fontSize.sm,
  },
});
export default DynamicTable;
