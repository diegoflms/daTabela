import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Header } from './Header';
import { colors } from '../../theme';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <View style={styles.container}>
      <Header />
      <View style={styles.body}>
        {children}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    width: '100%',
    height: '100%',
  },
  body: {
    flex: 1,
    width: '100%',
  },
});
export default AppShell;
