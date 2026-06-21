import React from 'react';
import { View, StyleSheet } from 'react-native';
import { TextInput } from '../../components/ui/TextInput';
import { Select } from '../../components/ui/Select';
import { spacing } from '../../theme';
import { useResponsive } from '../../hooks/useResponsive';

interface PlayerFiltersProps {
  searchQuery: string;
  onSearchChange: (text: string) => void;
  selectedTeam: string | number;
  onTeamChange: (val: any) => void;
  teamOptions: { label: string; value: string | number }[];
}

export const PlayerFilters: React.FC<PlayerFiltersProps> = ({
  searchQuery,
  onSearchChange,
  selectedTeam,
  onTeamChange,
  teamOptions,
}) => {
  const { isMobile } = useResponsive();

  return (
    <View style={[styles.container, isMobile && styles.containerColumn]}>
      <TextInput
        value={searchQuery}
        onChangeText={onSearchChange}
        placeholder="Buscar jogador por nome..."
        style={styles.searchInput}
      />
      <View style={styles.selectsRow}>
        <Select
          placeholder="Time"
          selectedValue={selectedTeam}
          onValueChange={onTeamChange}
          options={teamOptions}
          variant="orange"
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: spacing.md,
    width: '100%',
    marginBottom: spacing.lg,
  },
  containerColumn: {
    flexDirection: 'column',
    alignItems: 'stretch',
  },
  searchInput: {
    flex: 2,
    marginBottom: 0,
  },
  selectsRow: {
    flex: 3,
    flexDirection: 'row',
    gap: spacing.sm,
  },
});
export default PlayerFilters;
