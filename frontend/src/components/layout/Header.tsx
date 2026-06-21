import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Platform, TextInput, Image } from 'react-native';
import { Link, useRouter } from 'expo-router';
import { colors, spacing, typography } from '../../theme';
import { NavLink } from '../navigation/NavLink';
import { useResponsive } from '../../hooks/useResponsive';

export const Header: React.FC = () => {
  const router = useRouter();
  const { isMobile } = useResponsive();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [galeriaOpen, setGaleriaOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const toggleMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const handleLogoPress = () => {
    setMobileMenuOpen(false);
    setGaleriaOpen(false);
    router.push('/');
  };

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    setMobileMenuOpen(false);
    router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
  };

  const handleAjuda = () => {
    alert(
      'daTabela NBB\n\nUse o campo de busca no cabeçalho ou pergunte ao daTabela AI na página "Ask AI" para consultar estatísticas históricas, recordes e resultados do NBB de forma instantânea!'
    );
  };

  const handleSobreNos = () => {
    alert(
      'Sobre o daTabela\n\nDesenvolvido para organizar e apresentar dados consolidados históricos e estatísticos de equipes, partidas e jogadores do Novo Basquete Brasil (NBB).'
    );
  };

  return (
    <View style={styles.headerContainer}>
      <View style={styles.headerContent}>
        {/* Logo */}
        <TouchableOpacity 
          style={styles.logoContainer} 
          onPress={handleLogoPress}
          activeOpacity={0.8}
        >
          <Image
            source={require('../../../assets/images/logo.png')}
            style={styles.logoImage}
            resizeMode="contain"
          />
          <Text style={styles.logoText}>
            <Text style={styles.logoHighlight}>da</Text>Tabela
          </Text>
        </TouchableOpacity>

        {/* Busca no cabeçalho (Desktop) */}
        {!isMobile && (
          <View style={styles.searchBarContainer}>
            <TextInput
              style={styles.headerSearchInput}
              placeholder="Procure por jogadores, times e partidas"
              placeholderTextColor="#999999"
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearch}
            />
            <TouchableOpacity style={styles.searchIconContainer} onPress={handleSearch}>
              <View style={{ width: 18, height: 18, justifyContent: 'center', alignItems: 'center', marginRight: 4 }}>
                <View style={{
                  width: 12,
                  height: 12,
                  borderRadius: 6,
                  borderWidth: 2,
                  borderColor: colors.secondary, // Laranja do tema
                  position: 'relative',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}>
                  <View style={{
                    position: 'absolute',
                    width: 2,
                    height: 5,
                    backgroundColor: colors.secondary,
                    transform: [{ rotate: '-45deg' }],
                    bottom: -3.5,
                    right: -3.5,
                  }} />
                </View>
              </View>
            </TouchableOpacity>
          </View>
        )}

        {/* Desktop Navigation */}
        {!isMobile && (
          <View style={styles.navLinks}>
            <NavLink href="/" label="Início" />
            
            {/* Dropdown Menu para Galeria */}
            <View style={styles.dropdownContainer}>
              <TouchableOpacity 
                style={styles.dropdownTrigger} 
                onPress={() => setGaleriaOpen(!galeriaOpen)}
                activeOpacity={0.8}
              >
                <Text style={styles.dropdownTriggerText}>
                  Galeria <Text style={styles.arrowSmall}>▼</Text>
                </Text>
              </TouchableOpacity>
              
              {galeriaOpen && (
                <View style={styles.dropdownMenu}>
                  <TouchableOpacity 
                    style={styles.dropdownItem}
                    onPress={() => {
                      setGaleriaOpen(false);
                      router.push('/teams');
                    }}
                  >
                    <Text style={styles.dropdownItemText}>Times</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.dropdownItem}
                    onPress={() => {
                      setGaleriaOpen(false);
                      router.push('/players');
                    }}
                  >
                    <Text style={styles.dropdownItemText}>Jogadores</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>

            <Link href={"/help" as any} asChild>
              <TouchableOpacity style={styles.navButton}>
                <Text style={styles.navButtonText}>Ajuda</Text>
              </TouchableOpacity>
            </Link>
          </View>
        )}

        {/* Mobile Hamburguer Button */}
        {isMobile && (
          <TouchableOpacity style={styles.menuButton} onPress={toggleMenu} activeOpacity={0.7}>
            <Text style={styles.menuIcon}>{mobileMenuOpen ? '✕' : '☰'}</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Mobile Dropdown Menu */}
      {isMobile && mobileMenuOpen && (
        <View style={styles.mobileMenu}>
          <NavLink href="/" label="Início" onPress={() => setMobileMenuOpen(false)} />
          <NavLink href="/teams" label="Times" onPress={() => setMobileMenuOpen(false)} />
          <NavLink href="/players" label="Jogadores" onPress={() => setMobileMenuOpen(false)} />
          <NavLink href="/search" label="Busca Global" onPress={() => setMobileMenuOpen(false)} />
          <NavLink href="/ask" label="Perguntar ao AI 💬" onPress={() => setMobileMenuOpen(false)} />
          
          <Link href={"/help" as any} asChild>
            <TouchableOpacity style={styles.mobileNavButton} onPress={() => setMobileMenuOpen(false)}>
              <Text style={styles.mobileNavButtonText}>Ajuda</Text>
            </TouchableOpacity>
          </Link>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  headerContainer: {
    backgroundColor: colors.primary,
    borderBottomWidth: 1,
    borderBottomColor: colors.primaryDark,
    width: '100%',
    zIndex: 1000,
    ...Platform.select({
      web: {
        position: 'sticky',
        top: 0,
      } as any,
    }),
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  headerContent: {
    height: 64,
    maxWidth: 1200,
    width: '100%',
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoImage: {
    width: 28,
    height: 28,
    marginRight: spacing.xs,
  },
  logoText: {
    fontSize: typography.fontSize.xl,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    letterSpacing: -0.5,
  },
  logoHighlight: {
    color: colors.secondary,
  },
  searchBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 6,
    width: 380,
    height: 38,
    paddingHorizontal: spacing.sm,
    position: 'relative',
  },
  headerSearchInput: {
    flex: 1,
    height: '100%',
    color: '#121212',
    fontSize: 14,
    paddingRight: 30,
    borderWidth: 0,
    ...Platform.select({
      web: {
        outlineStyle: 'none',
      } as any,
    }),
  },
  searchIconContainer: {
    position: 'absolute',
    right: 10,
    justifyContent: 'center',
    height: '100%',
  },
  searchIcon: {
    fontSize: 14,
  },
  navLinks: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dropdownContainer: {
    position: 'relative',
    marginHorizontal: spacing.xs,
    zIndex: 2000,
  },
  dropdownTrigger: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 6,
  },
  dropdownTriggerText: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  arrowSmall: {
    fontSize: 10,
  },
  dropdownMenu: {
    position: 'absolute',
    top: 36,
    left: 0,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    width: 130,
    paddingVertical: spacing.xs,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
  dropdownItem: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  dropdownItemText: {
    color: colors.text,
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
  },
  navButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 6,
    marginHorizontal: spacing.xs,
  },
  navButtonText: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  menuButton: {
    padding: spacing.sm,
  },
  menuIcon: {
    fontSize: 24,
    color: colors.textLight,
  },
  mobileMenu: {
    backgroundColor: colors.primaryDark,
    paddingVertical: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.1)',
    width: '100%',
  },
  mobileNavButton: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
  },
  mobileNavButtonText: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
    color: 'rgba(255, 255, 255, 0.8)',
  },
});
export default Header;
