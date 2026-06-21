import React from 'react';
import { ScrollView, StyleSheet, View, ViewStyle, SafeAreaView } from 'react-native';
import { colors, spacing } from '../../theme';

interface PageContainerProps {
  children: React.ReactNode;
  style?: ViewStyle;
  contentContainerStyle?: ViewStyle;
  scrollable?: boolean;
}

export const PageContainer: React.FC<PageContainerProps> = ({
  children,
  style,
  contentContainerStyle,
  scrollable = true,
}) => {
  const innerContent = (
    <View style={[styles.inner, style]}>
      {children}
    </View>
  );

  return (
    <SafeAreaView style={styles.safe}>
      {scrollable ? (
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={[styles.scrollContent, contentContainerStyle]}
          showsVerticalScrollIndicator={true}
        >
          {innerContent}
        </ScrollView>
      ) : (
        <View style={[styles.container, contentContainerStyle]}>{innerContent}</View>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    alignItems: 'center',
  },
  container: {
    flex: 1,
    alignItems: 'center',
    width: '100%',
  },
  inner: {
    width: '100%',
    maxWidth: 1200,
    padding: spacing.lg,
    flexGrow: 1,
  },
});
export default PageContainer;
