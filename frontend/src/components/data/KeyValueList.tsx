import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme';
import { formatColumnLabel } from '../../utils/labels';
import { formatCellValue } from '../../utils/formatters';

interface KeyValueItem {
  key: string;
  value: any;
  label?: string;
}

interface KeyValueListProps {
  items: KeyValueItem[];
  title?: string;
  style?: ViewStyle;
}

export const KeyValueList: React.FC<KeyValueListProps> = ({ items, title, style }) => {
  const activeItems = items.filter(
    (item) => item.value !== null && item.value !== undefined && item.value !== ''
  );

  return (
    <View style={[styles.container, style]}>
      {title && (
        <View style={styles.titleContainer}>
          <Text style={styles.titleText}>{title}</Text>
        </View>
      )}
      <View style={styles.list}>
        {activeItems.length > 0 ? (
          activeItems.map((item, idx) => (
            <View
              key={`kv-${item.key}-${idx}`}
              style={[
                styles.itemRow,
                idx === activeItems.length - 1 && styles.lastItemRow,
              ]}
            >
              <Text style={styles.label}>
                {item.label || formatColumnLabel(item.key)}
              </Text>
              <Text style={styles.value}>
                {formatCellValue(item.value, item.key)}
              </Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>Sem informações disponíveis.</Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  titleContainer: {
    backgroundColor: colors.secondary,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 6,
    marginBottom: spacing.sm,
  },
  titleText: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  list: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    backgroundColor: colors.surface,
    overflow: 'hidden',
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.surface,
  },
  lastItemRow: {
    borderBottomWidth: 0,
  },
  label: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.medium,
    color: colors.textSecondary,
  },
  value: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
  },
  emptyText: {
    padding: spacing.md,
    color: colors.textMuted,
    fontSize: typography.fontSize.sm,
    textAlign: 'center',
  },
});
export default KeyValueList;
