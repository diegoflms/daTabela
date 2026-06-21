import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { colors, spacing, typography } from '../../theme';
import { formatCellValue } from '../../utils/formatters';
import { Link } from 'expo-router';

interface RankingTableProps {
  items: any[];
  metricKey: string;
  type: 'players' | 'teams';
}

export const RankingTable: React.FC<RankingTableProps> = ({ items, metricKey, type }) => {
  const isPlayer = type === 'players';

  return (
    <ScrollView horizontal={true} showsHorizontalScrollIndicator={true} style={styles.scroll}>
      <View style={styles.tableContainer}>
        {/* Header */}
        <View style={styles.tableRowHeader}>
          <View style={[styles.cellHeader, styles.rankCell]}>
            <Text style={styles.cellHeaderText}>#</Text>
          </View>
          <View style={[styles.cellHeader, styles.nameCell]}>
            <Text style={styles.cellHeaderText}>
              {isPlayer ? 'JOGADOR' : 'EQUIPE'}
            </Text>
          </View>
          {isPlayer && (
            <View style={[styles.cellHeader, styles.teamCell]}>
              <Text style={styles.cellHeaderText}>TIME</Text>
            </View>
          )}
          <View style={[styles.cellHeader, styles.valueCell]}>
            <Text style={styles.cellHeaderText}>VALOR</Text>
          </View>
        </View>

        {/* Rows */}
        {items.length > 0 ? (
          items.map((item, idx) => {
            const id = isPlayer ? item.player_id : item.team_id;
            const name = isPlayer 
              ? (item.player_name || item.entity_player_name) 
              : (item.team_name || item.entity_team_name);
            const team = item.team_name || item.entity_team_name || '-';
            const val = item.ranking_value;
            const linkPath = isPlayer ? `/players/${id}` : `/teams/${id}`;

            return (
              <Link key={`rank-row-${id}-${idx}`} href={linkPath as any} asChild>
                <TouchableOpacity 
                  style={StyleSheet.flatten([
                    styles.tableRow,
                    idx % 2 === 1 && styles.tableRowAlternate,
                    idx === items.length - 1 && styles.lastRow,
                  ])}
                  activeOpacity={0.7}
                >
                  <View style={[styles.cell, styles.rankCell]}>
                    <Text style={[styles.rankText, idx === 0 && styles.firstPlace]}>
                      {idx + 1}
                    </Text>
                  </View>
                  
                  <View style={[styles.cell, styles.nameCell]}>
                    <Text style={styles.nameText} numberOfLines={1}>
                      {name || 'Desconhecido'}
                    </Text>
                  </View>

                  {isPlayer && (
                    <View style={[styles.cell, styles.teamCell]}>
                      <Text style={styles.teamText} numberOfLines={1}>
                        {team}
                      </Text>
                    </View>
                  )}

                  <View style={[styles.cell, styles.valueCell]}>
                    <Text style={styles.valueText}>
                      {formatCellValue(val, metricKey)}
                    </Text>
                  </View>
                </TouchableOpacity>
              </Link>
            );
          })
        ) : (
          <View style={styles.noDataContainer}>
            <Text style={styles.noDataText}>Nenhum registro para exibir.</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scroll: {
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
    backgroundColor: colors.surfaceSecondary,
    borderBottomWidth: 2,
    borderBottomColor: colors.border,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  cellHeader: {
    justifyContent: 'center',
    paddingHorizontal: spacing.xs,
  },
  cellHeaderText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    alignItems: 'center',
  },
  tableRowAlternate: {
    backgroundColor: '#F8FAFC',
  },
  lastRow: {
    borderBottomWidth: 0,
  },
  cell: {
    justifyContent: 'center',
    paddingHorizontal: spacing.xs,
  },
  rankCell: {
    width: 50,
    alignItems: 'center',
  },
  rankText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.medium,
    color: colors.textSecondary,
  },
  firstPlace: {
    color: colors.secondaryDark,
    fontFamily: typography.fontFamily.bold,
  },
  nameCell: {
    width: 220,
  },
  nameText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
  },
  teamCell: {
    width: 160,
  },
  teamText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  valueCell: {
    width: 100,
    alignItems: 'flex-end',
  },
  valueText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.primary,
  },
  noDataContainer: {
    padding: spacing.xl,
    alignItems: 'center',
    width: '100%',
  },
  noDataText: {
    color: colors.textMuted,
    fontSize: typography.fontSize.sm,
  },
});
export default RankingTable;
