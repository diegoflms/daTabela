import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, FlatList, StyleSheet, Pressable, Platform } from 'react-native';
import { colors, spacing, typography } from '../../theme';

interface Option {
  label: string;
  value: string | number;
}

interface SelectProps {
  label?: string;
  selectedValue: string | number;
  onValueChange: (value: any) => void;
  options: Option[];
  placeholder?: string;
  variant?: 'default' | 'orange';
}

export const Select: React.FC<SelectProps> = ({
  label,
  selectedValue,
  onValueChange,
  options,
  placeholder = 'Selecione...',
  variant = 'default',
}) => {
  const [modalVisible, setModalVisible] = useState(false);

  const selectedOption = options.find((opt) => opt.value === selectedValue);

  const handleSelect = (value: any) => {
    onValueChange(value);
    setModalVisible(false);
  };

  // Na Web podemos renderizar um select nativo para melhor UX do browser
  if (Platform.OS === 'web') {
    return (
      <View style={styles.container}>
        {label && <Text style={styles.label}>{label}</Text>}
        <select
          value={selectedValue}
          onChange={(e) => {
            const val = e.target.value;
            // Tenta converter para número se for numérico
            const parsedVal = !isNaN(Number(val)) && val !== '' ? Number(val) : val;
            onValueChange(parsedVal);
          }}
          style={{
            height: 48,
            backgroundColor: variant === 'orange' ? colors.secondary : colors.surface,
            borderWidth: 1,
            borderStyle: 'solid',
            borderColor: variant === 'orange' ? colors.secondaryDark : colors.border,
            borderRadius: 8,
            paddingLeft: spacing.md,
            paddingRight: spacing.md,
            fontSize: typography.fontSize.md,
            color: variant === 'orange' ? colors.textLight : colors.text,
            width: '100%',
            outline: 'none',
            cursor: 'pointer',
            fontFamily: 'Inter, sans-serif',
            fontWeight: variant === 'orange' ? 'bold' : 'normal',
          }}
        >
          <option value="" style={{ backgroundColor: colors.surface, color: colors.text }}>
            {placeholder}
          </option>
          {options.map((opt) => (
            <option 
              key={opt.value} 
              value={opt.value}
              style={{ backgroundColor: colors.surface, color: colors.text }}
            >
              {opt.label}
            </option>
          ))}
        </select>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {label && <Text style={styles.label}>{label}</Text>}
      <TouchableOpacity
        style={[styles.trigger, variant === 'orange' && styles.triggerOrange]}
        onPress={() => setModalVisible(true)}
        activeOpacity={0.7}
      >
        <Text style={[
          styles.triggerText,
          variant === 'orange' && styles.triggerTextOrange,
          !selectedOption && styles.placeholderText,
          !selectedOption && variant === 'orange' && { color: 'rgba(255, 255, 255, 0.8)' }
        ]}>
          {selectedOption ? selectedOption.label : placeholder}
        </Text>
        <Text style={[styles.arrow, variant === 'orange' && styles.arrowOrange]}>▼</Text>
      </TouchableOpacity>

      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setModalVisible(false)}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{label || 'Selecione uma opção'}</Text>
            <FlatList
              data={options}
              keyExtractor={(item) => String(item.value)}
              renderItem={({ item }) => (
                <TouchableOpacity
                   style={[
                    styles.optionItem,
                    item.value === selectedValue && styles.selectedOptionItem,
                  ]}
                  onPress={() => handleSelect(item.value)}
                >
                  <Text
                    style={[
                      styles.optionText,
                      item.value === selectedValue && styles.selectedOptionText,
                    ]}
                  >
                    {item.label}
                  </Text>
                </TouchableOpacity>
              )}
            />
          </View>
        </Pressable>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
    flex: 1,
    minWidth: 120,
  },
  label: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.medium,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  trigger: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    height: 48,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  triggerOrange: {
    backgroundColor: colors.secondary,
    borderColor: colors.secondaryDark,
  },
  triggerText: {
    fontSize: typography.fontSize.md,
    color: colors.text,
  },
  triggerTextOrange: {
    color: colors.textLight,
    fontFamily: typography.fontFamily.bold,
  },
  placeholderText: {
    color: colors.textMuted,
  },
  arrow: {
    fontSize: 10,
    color: colors.textSecondary,
  },
  arrowOrange: {
    color: colors.textLight,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: colors.overlay,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  modalContent: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    width: '100%',
    maxHeight: 400,
    padding: spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
  },
  modalTitle: {
    fontSize: typography.fontSize.lg,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
    marginBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: spacing.sm,
  },
  optionItem: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    borderRadius: 6,
  },
  selectedOptionItem: {
    backgroundColor: colors.primaryLight,
  },
  optionText: {
    fontSize: typography.fontSize.md,
    color: colors.text,
  },
  selectedOptionText: {
    color: colors.primary,
    fontFamily: typography.fontFamily.medium,
  },
});
export default Select;
