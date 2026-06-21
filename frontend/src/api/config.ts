import { Platform } from 'react-native';

const getApiUrl = () => {
  // Se estiver explicitamente definida no .env, use-a
  if (process.env.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL;
  }
  
  // Fallbacks de desenvolvimento baseados na plataforma
  if (Platform.OS === 'web') {
    return 'http://127.0.0.1:8000';
  }
  
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000'; // IP padrão para o Host do emulador Android
  }
  
  // Para iOS (simulador usa o localhost do host mac)
  return 'http://127.0.0.1:8000';
};

export const API_URL = getApiUrl();
console.log('[API_URL Configured]:', API_URL);
