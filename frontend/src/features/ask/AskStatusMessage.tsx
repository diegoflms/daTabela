import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { colors, spacing, typography } from '../../theme';
import { AskStatus } from '../../types/ask';

interface AskStatusMessageProps {
  status: AskStatus;
  message?: string;
  supportedExamples?: string[];
  onSelectExample: (example: string) => void;
}

export const AskStatusMessage: React.FC<AskStatusMessageProps> = ({
  status,
  message,
  supportedExamples = [],
  onSelectExample,
}) => {
  const isUnsupported = status === 'unsupported';
  const displayMsg = message || (isUnsupported 
    ? 'Desculpe, ainda não sei interpretar essa pergunta no MVP.' 
    : 'Não encontramos nenhum dado correspondente à sua pergunta.');

  return (
    <View style={[styles.container, isUnsupported ? styles.unsupportedBg : styles.notFoundBg]}>
      <Text style={styles.icon}>{isUnsupported ? '🤖' : '🔍'}</Text>
      <Text style={[styles.title, isUnsupported ? styles.unsupportedTitle : styles.notFoundTitle]}>
        {isUnsupported ? 'Pergunta Não Suportada' : 'Nenhum Dado Encontrado'}
      </Text>
      <Text style={styles.message}>{displayMsg}</Text>

      {isUnsupported && supportedExamples.length > 0 && (
        <View style={styles.examplesSection}>
          <Text style={styles.examplesTitle}>Perguntas que eu sei responder:</Text>
          <View style={styles.examplesList}>
            {supportedExamples.map((ex, idx) => (
              <TouchableOpacity
                key={`supported-ex-${idx}`}
                style={styles.exampleItem}
                onPress={() => onSelectExample(ex)}
                activeOpacity={0.7}
              >
                <Text style={styles.exampleText}>• {ex}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderWidth: 1,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
    width: '100%',
    marginVertical: spacing.md,
  },
  unsupportedBg: {
    backgroundColor: '#EBF5FB', // Azul claro para não suportado
    borderColor: 'rgba(59, 130, 246, 0.2)',
  },
  notFoundBg: {
    backgroundColor: '#FDEDEC', // Vermelho claro para não encontrado
    borderColor: 'rgba(239, 68, 68, 0.2)',
  },
  icon: {
    fontSize: 40,
    marginBottom: spacing.xs,
  },
  title: {
    fontSize: typography.fontSize.lg,
    fontFamily: typography.fontFamily.bold,
    marginBottom: spacing.xs,
  },
  unsupportedTitle: {
    color: colors.info,
  },
  notFoundTitle: {
    color: colors.error,
  },
  message: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.md,
    lineHeight: typography.lineHeight.sm,
    maxWidth: 500,
  },
  examplesSection: {
    width: '100%',
    borderTopWidth: 1,
    borderTopColor: 'rgba(59, 130, 246, 0.1)',
    paddingTop: spacing.md,
  },
  examplesTitle: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  examplesList: {
    gap: spacing.xs,
  },
  exampleItem: {
    paddingVertical: spacing.xs,
  },
  exampleText: {
    fontSize: typography.fontSize.sm,
    color: colors.info,
    fontFamily: typography.fontFamily.medium,
  },
});
export default AskStatusMessage;
