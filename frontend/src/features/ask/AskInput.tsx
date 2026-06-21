import React from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { colors, spacing, typography } from '../../theme';

interface AskInputProps {
  value: string;
  onChangeText: (text: string) => void;
  onSubmit: () => void;
  loading?: boolean;
}

export const AskInput: React.FC<AskInputProps> = ({
  value,
  onChangeText,
  onSubmit,
  loading = false,
}) => {
  return (
    <View style={styles.container}>
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder="Pergunte ex: 'matheusinho ultimos 5 jogos'"
        placeholderTextColor={colors.textMuted}
        style={styles.input}
        onSubmitEditing={onSubmit}
        editable={!loading}
        autoCapitalize="none"
      />
      <TouchableOpacity
        style={[styles.button, (!value.trim() || loading) && styles.buttonDisabled]}
        onPress={onSubmit}
        disabled={!value.trim() || loading}
        activeOpacity={0.8}
      >
        <Text style={styles.buttonText}>{loading ? '...' : 'Enviar ➔'}</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 2,
    borderColor: colors.primary,
    borderRadius: 12,
    paddingLeft: spacing.md,
    paddingRight: spacing.xs,
    height: 56,
    width: '100%',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
    marginVertical: spacing.md,
  },
  input: {
    flex: 1,
    height: '100%',
    fontSize: typography.fontSize.md,
    color: colors.text,
    outlineWidth: 0, // Remove contorno azul no navegador web
    fontFamily: typography.fontFamily.regular,
  } as any,
  button: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    height: 44,
    paddingHorizontal: spacing.lg,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: colors.border,
  },
  buttonText: {
    color: colors.textLight,
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.sm,
  },
});
export default AskInput;
