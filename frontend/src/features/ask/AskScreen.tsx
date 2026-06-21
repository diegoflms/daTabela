import React, { useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { AskInput } from './AskInput';
import { AskExamples } from './AskExamples';
import { AskResult } from './AskResult';
import { AskClarification } from './AskClarification';
import { AskStatusMessage } from './AskStatusMessage';
import { colors, spacing, typography } from '../../theme';
import { askQuestion } from '../../api/ask';
import { useAsync } from '../../hooks/useAsync';

export const AskScreen: React.FC = () => {
  const [question, setQuestion] = useState('');
  const { data: result, loading, error, execute: runAsk } = useAsync(askQuestion);

  const handleSubmit = () => {
    if (!question.trim()) return;
    runAsk(question.trim()).catch(() => {});
  };

  const handleSelectExample = (example: string) => {
    setQuestion(example);
    runAsk(example).catch(() => {});
  };

  const handleSelectCandidate = (candidateName: string) => {
    const originalQuestion = question;
    const playerQuery = result?.interpreted_as?.player_query || '';
    
    let newQuestion = originalQuestion;
    if (playerQuery && candidateName) {
      // Substituição case-insensitive inteligente do termo de pesquisa pelo nome exato
      const regex = new RegExp(playerQuery, 'gi');
      newQuestion = originalQuestion.replace(regex, candidateName);
    } else {
      // Se não conseguir mapear, faz a busca pelo nome exato do candidato
      newQuestion = `${candidateName} ultimos ${result?.interpreted_as?.last_n_games || 5} jogos`;
    }

    setQuestion(newQuestion);
    runAsk(newQuestion).catch(() => {});
  };

  return (
    <AppShell>
      <PageContainer>
        <View style={styles.header}>
          <Text style={styles.title}>daTabela AI Ask 💬</Text>
          <Text style={styles.subtitle}>
            Consulte estatísticas, recordes e confrontos históricos do NBB de forma instantânea.
          </Text>
        </View>

        <AskInput
          value={question}
          onChangeText={setQuestion}
          onSubmit={handleSubmit}
          loading={loading}
        />

        {/* Sugestões de perguntas rápidas */}
        {!loading && !result && (
          <AskExamples onSelect={handleSelectExample} />
        )}

        {/* Estado de Carregamento */}
        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>
              🤖 Interpretando pergunta e consultando banco de dados SQLite...
            </Text>
          </View>
        )}

        {/* Estado de Erro na Conexão/API */}
        {error && !loading && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorIcon}>⚠️</Text>
            <View style={styles.errorContent}>
              <Text style={styles.errorTitle}>Falha na consulta</Text>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          </View>
        )}

        {/* Renderização condicional do resultado baseado no status */}
        {result && !loading && (
          <View style={styles.resultContainer}>
            {result.status === 'ok' && (
              <AskResult result={result} />
            )}

            {result.status === 'needs_clarification' && (
              <AskClarification
                candidates={result.candidates || []}
                onSelectCandidate={handleSelectCandidate}
              />
            )}

            {(result.status === 'unsupported' || result.status === 'not_found') && (
              <AskStatusMessage
                status={result.status}
                message={result.message}
                supportedExamples={result.supported_examples}
                onSelectExample={handleSelectExample}
              />
            )}
          </View>
        )}
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  header: {
    marginBottom: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontFamily: typography.fontFamily.bold,
    color: colors.primaryDark,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    lineHeight: typography.lineHeight.sm,
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xxl,
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    marginVertical: spacing.md,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.medium,
    textAlign: 'center',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FDEDEC',
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.2)',
    borderRadius: 12,
    padding: spacing.lg,
    marginVertical: spacing.md,
  },
  errorIcon: {
    fontSize: 24,
    marginRight: spacing.md,
  },
  errorContent: {
    flex: 1,
  },
  errorTitle: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.error,
    marginBottom: 2,
  },
  errorText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: typography.lineHeight.sm,
  },
  resultContainer: {
    width: '100%',
  },
});
export default AskScreen;
