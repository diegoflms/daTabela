import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { AppShell } from '../components/layout/AppShell';
import { PageContainer } from '../components/layout/PageContainer';
import { colors, spacing, typography } from '../theme';

interface FAQItem {
  question: string;
  answer: string;
}

const FAQ_ITEMS: FAQItem[] = [
  {
    question: "O que é o daTabela NBB?",
    answer: "O daTabela NBB é um portal esportivo dedicado a organizar e apresentar dados consolidados históricos e estatísticos do Novo Basquete Brasil (NBB). Nosso objetivo é facilitar o acesso aos dados do campeonato de basquete de maneira simples e interativa."
  },
  {
    question: "Como posso buscar por um jogador ou time específico?",
    answer: "Use o campo de pesquisa no topo da página para digitar o nome de qualquer atleta ou clube. O sistema exibirá a página de perfil correspondente com as informações de médias e históricos."
  },
  {
    question: "O que é a busca por perguntas (Ask)?",
    answer: "É uma ferramenta de busca do portal que permite fazer perguntas diretas sobre o campeonato (como 'Quem fez mais pontos na última rodada?'). O portal processa a sua pergunta e mostra a resposta em formato de tabela."
  },
  {
    question: "Os dados e estatísticas são atualizados constantemente?",
    answer: "Sim! O portal é atualizado de forma contínua com os dados de todas as partidas oficiais do NBB. Assim que um jogo é concluído e seus dados de súmula oficial são registrados, os históricos de equipes e médias de jogadores são recalculados instantaneamente."
  },
  {
    question: "Quero mais informações. O que fazer?",
    answer: "Se você quiser saber mais, tirar dúvidas, dar sugestões ou nos enviar feedback, mande um e-mail para databela@gmail.com. Estamos sempre à disposição para ajudar!"
  }
];

export const HelpScreen: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleAccordion = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <AppShell>
      <PageContainer>
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          <View style={styles.headerContainer}>
            <Text style={styles.title}>Central de Ajuda</Text>
            <Text style={styles.subtitle}>
              Dúvidas frequentes sobre o uso da plataforma. Caso precise de suporte ou mais informações, entre em contato pelo e-mail{' '}
              <Text style={styles.email}>databela@gmail.com</Text>
            </Text>
          </View>

          <View style={styles.faqList}>
            {FAQ_ITEMS.map((item, index) => {
              const isOpen = openIndex === index;
              return (
                <View key={`faq-${index}`} style={[styles.accordionItem, isOpen && styles.accordionItemOpen]}>
                  <TouchableOpacity
                    style={styles.accordionHeader}
                    onPress={() => toggleAccordion(index)}
                    activeOpacity={0.8}
                  >
                    <Text style={[styles.questionText, isOpen && styles.questionTextOpen]}>{item.question}</Text>
                    <View style={[styles.chevronBg, isOpen && styles.chevronBgOpen]}>
                      <Text style={styles.chevron}>{isOpen ? '▲' : '▼'}</Text>
                    </View>
                  </TouchableOpacity>
                  {isOpen && (
                    <View style={styles.answerContainer}>
                      <Text style={styles.answerText}>{item.answer}</Text>
                    </View>
                  )}
                </View>
              );
            })}
          </View>
        </ScrollView>
      </PageContainer>
    </AppShell>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    paddingBottom: spacing.xxl,
    alignItems: 'center',
    width: '100%',
  },
  headerContainer: {
    alignItems: 'center',
    marginTop: spacing.xxl,
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.md,
  },
  title: {
    fontSize: 32,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  subtitle: {
    fontSize: 16,
    fontFamily: typography.fontFamily.regular,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
    maxWidth: 650,
  },
  email: {
    color: colors.primary, // Laranja do tema principal
    fontFamily: typography.fontFamily.bold,
  },
  faqList: {
    width: '100%',
    maxWidth: 800,
    gap: spacing.md,
    paddingHorizontal: spacing.md,
  },
  accordionItem: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
  },
  accordionItemOpen: {
    borderColor: 'rgba(255, 122, 0, 0.4)', // Sombra ou brilho laranja sutil ao abrir
  },
  accordionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xl,
    width: '100%',
  },
  questionText: {
    color: colors.text,
    fontSize: 16,
    fontFamily: typography.fontFamily.bold,
    flex: 1,
    paddingRight: spacing.md,
  },
  questionTextOpen: {
    color: colors.primary, // Transiciona para laranja quando aberto
  },
  chevronBg: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  chevronBgOpen: {
    backgroundColor: 'rgba(255, 122, 0, 0.1)',
  },
  chevron: {
    color: colors.textSecondary,
    fontSize: 10,
  },
  answerContainer: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.lg,
  },
  answerText: {
    color: colors.textSecondary,
    fontSize: 15,
    fontFamily: typography.fontFamily.regular,
    lineHeight: 22,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.md,
  },
});

export default HelpScreen;
