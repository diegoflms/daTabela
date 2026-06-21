import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AppShell } from '../../components/layout/AppShell';
import { PageContainer } from '../../components/layout/PageContainer';
import { TextInput } from '../../components/ui/TextInput';
import { Button } from '../../components/ui/Button';
import { LoadingState } from '../../components/ui/LoadingState';
import { ErrorState } from '../../components/ui/ErrorState';
import { SearchResults } from './SearchResults';
import { globalSearch } from '../../api/search';
import { useAsync } from '../../hooks/useAsync';
import { colors, spacing, typography } from '../../theme';
import { useLocalSearchParams } from 'expo-router';

export const SearchScreen: React.FC = () => {
  const params = useLocalSearchParams();
  const [query, setQuery] = useState('');
  const { data: results, loading, error, execute: runSearch } = useAsync(globalSearch);

  // Se vier termo de busca via parâmetro de rota (ex: redirecionado do cabeçalho)
  useEffect(() => {
    if (params.q) {
      const qVal = String(params.q);
      setQuery(qVal);
      runSearch(qVal).catch(() => {});
    }
  }, [params.q, runSearch]);

  const handleSearch = () => {
    if (!query.trim()) return;
    runSearch(query.trim()).catch(() => {});
  };

  return (
    <AppShell>
      <PageContainer>
        <View style={styles.header}>
          <Text style={styles.title}>Busca Global</Text>
          <Text style={styles.subtitle}>
            Procure por jogadores, times e partidas do NBB cadastrados no SQLite.
          </Text>
        </View>

        <View style={styles.searchBar}>
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Digite o nome do jogador, time ou arena..."
            style={styles.searchInput}
            onSubmitEditing={handleSearch}
          />
          <Button
            title="Buscar"
            onPress={handleSearch}
            loading={loading}
            style={styles.searchButton}
          />
        </View>

        {loading && <LoadingState message="Buscando registros..." />}

        {error && !loading && (
          <ErrorState message={error} onRetry={handleSearch} />
        )}

        {!loading && !error && results && (
          <SearchResults results={results} query={query} />
        )}
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  header: {
    marginBottom: spacing.lg,
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
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.sm,
    width: '100%',
    marginBottom: spacing.xl,
  },
  searchInput: {
    flex: 1,
    marginBottom: 0,
  },
  searchButton: {
    height: 48,
  },
});
export default SearchScreen;
